"use client";

import { Suspense, useCallback, useEffect, useRef, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { getWsMysteryUrl } from "@/lib/api";

interface PlayerInfo {
  id: string;
  name: string;
  char_id: string | null;
  is_ai: boolean;
  color: number[] | null;
}

interface ChatMessage {
  type: "narration" | "chat" | "clue" | "phase" | "truth";
  player_id?: string;
  char_id?: string;
  char_name?: string;
  message?: string;
  text?: string;
  speaker?: string;
  is_ai?: boolean;
  color?: number[];
  clue?: {
    id: string;
    name: string;
    description: string;
    inference: string;
  };
  phase?: string;
  description?: string;
}

function MysteryGameContent() {
  const router = useRouter();
  const params = useParams();
  const roomId = params.roomId as string;

  const [ws, setWs] = useState<WebSocket | null>(null);
  const [playerId, setPlayerId] = useState("");
  const [playerName, setPlayerName] = useState("");
  const [name, setName] = useState("");
  const [joined, setJoined] = useState(false);
  const [phase, setPhase] = useState("lobby");
  const [players, setPlayers] = useState<PlayerInfo[]>([]);
  const [mode, setMode] = useState<"solo" | "multi">("multi");
  const [host, setHost] = useState("");
  const [charId, setCharId] = useState<string | null>(null);
  const [charName, setCharName] = useState("");
  const [privateScript, setPrivateScript] = useState("");
  const [charColor, setCharColor] = useState<number[]>([200, 200, 200]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [error, setError] = useState("");
  const [availableRoles, setAvailableRoles] = useState<
    { char_id: string; name: string; surface_identity: string; color: number[] }[]
  >([]);
  const [showScript, setShowScript] = useState(false);
  const [selectedRole, setSelectedRole] = useState<string | null>(null);
  const [votes, setVotes] = useState<Record<string, string>>({});
  const [votePhase, setVotePhase] = useState<string | null>(null);

  const chatEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const connect = useCallback(() => {
    if (!name.trim()) {
      setError("Enter your name");
      return;
    }
    setError("");

    const wsUrl = getWsMysteryUrl(roomId);
    const websocket = new WebSocket(wsUrl);
    setWs(websocket);

    websocket.onopen = () => {
      websocket.send(JSON.stringify({ type: "join", name: name.trim() }));
    };

    websocket.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);

        switch (msg.type) {
          case "lobby":
            setMode(msg.mode || "multi");
            setHost(msg.host || "");
            setPlayers(msg.players || []);
            break;

          case "joined":
            setPlayerId(msg.player_id);
            setJoined(true);
            break;

          case "role_select":
            setAvailableRoles(msg.available_roles || []);
            setPhase("role_select");
            break;

          case "role_selected":
            setSelectedRole(msg.char_id);
            break;

          case "role_assigned":
            setCharId(msg.char_id);
            setCharName(msg.name);
            setCharColor(msg.color || [200, 200, 200]);
            setPrivateScript(msg.script || "");
            setSelectedRole(msg.char_id);
            break;

          case "phase":
            setPhase(msg.phase);
            setVotePhase(null);
            setMessages((prev) => [
              ...prev,
              { type: "phase", phase: msg.phase, description: msg.description },
            ]);
            break;

          case "narration":
            setMessages((prev) => [
              ...prev,
              { type: "narration", text: msg.text, speaker: msg.speaker },
            ]);
            break;

          case "chat":
            setMessages((prev) => [
              ...prev,
              {
                type: "chat",
                player_id: msg.player_id,
                char_id: msg.char_id,
                char_name: msg.char_name,
                message: msg.message,
                is_ai: msg.is_ai,
                color: msg.color,
              },
            ]);
            break;

          case "clue":
            setMessages((prev) => [
              ...prev,
              { type: "clue", clue: msg.clue },
            ]);
            break;

          case "vote_result":
            setMessages((prev) => [
              ...prev,
              {
                type: "narration",
                text: `搜证结果：宿舍搜查 → ${msg.dorm_target}，身上搜查 → ${msg.body_target}`,
                speaker: "host",
              },
            ]);
            break;

          case "accuse_result":
            setMessages((prev) => [
              ...prev,
              {
                type: "narration",
                text: `投票结果：${msg.winner_name} 被指认为鱼妖。${msg.correct ? "猜对了！" : "猜错了..."}`,
                speaker: "host",
              },
            ]);
            break;

          case "truth":
            setMessages((prev) => [
              ...prev,
              { type: "truth", text: msg.text },
            ]);
            break;

          case "error":
            setError(msg.message || "Error");
            break;
        }
      } catch {
        /* ignore parse errors */
      }
    };

    websocket.onerror = () => setError("Connection failed");
    websocket.onclose = () => {
      if (!joined) setError("Disconnected");
    };
  }, [roomId, name, joined]);

  const sendMessage = useCallback(() => {
    if (!ws || ws.readyState !== WebSocket.OPEN || !input.trim()) return;
    ws.send(JSON.stringify({ type: "chat", message: input.trim() }));
    setInput("");
    inputRef.current?.focus();
  }, [ws, input]);

  const sendVote = useCallback(
    (voteType: string, targetCharId: string) => {
      if (!ws || ws.readyState !== WebSocket.OPEN) return;
      ws.send(
        JSON.stringify({ type: voteType, char_id: targetCharId })
      );
      setVotes((prev) => ({ ...prev, [voteType]: targetCharId }));
    },
    [ws]
  );

  const startGame = useCallback(() => {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    if (mode === "solo" && selectedRole) {
      ws.send(JSON.stringify({ type: "select_role", char_id: selectedRole }));
    }
    ws.send(JSON.stringify({ type: "start_game" }));
  }, [ws, mode, selectedRole]);

  const endDiscuss = useCallback(() => {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    ws.send(JSON.stringify({ type: "end_discuss" }));
  }, [ws]);

  // Not joined yet — show name input
  if (!joined) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[600px] bg-gray-900 rounded-lg border border-gray-700 p-8">
        <h2 className="text-2xl font-bold text-white mb-2">相府鱼美人</h2>
        <p className="text-gray-400 mb-6">
          房间:{" "}
          <span className="font-mono text-indigo-400 text-lg">{roomId}</span>
        </p>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && connect()}
          placeholder="你的名字"
          maxLength={20}
          className="px-4 py-2 rounded bg-gray-800 border border-gray-600 text-white mb-4 w-64 text-center"
        />
        <button
          onClick={connect}
          className="px-6 py-2 rounded-lg bg-indigo-600 text-white font-bold hover:bg-indigo-500"
        >
          加入
        </button>
        {error && <p className="text-red-400 text-sm mt-2">{error}</p>}
      </div>
    );
  }

  // Role selection (solo mode)
  if (phase === "role_select" && availableRoles.length > 0 && !charId) {
    return (
      <div className="max-w-lg mx-auto bg-gray-900 rounded-lg border border-gray-700 p-8">
        <h2 className="text-2xl font-bold text-white mb-2">选择你的角色</h2>
        <p className="text-gray-400 text-sm mb-6">
          选择你想要扮演的角色
        </p>
        <div className="space-y-3">
          {availableRoles.map((role) => (
            <button
              key={role.char_id}
              onClick={() => setSelectedRole(role.char_id)}
              className={`w-full text-left px-6 py-4 rounded-lg border transition ${
                selectedRole === role.char_id
                  ? "bg-indigo-600/20 border-indigo-500"
                  : "bg-gray-800 border-gray-600 hover:bg-gray-700"
              }`}
            >
              <div className="flex items-center gap-3">
                <div
                  className="w-4 h-4 rounded-full"
                  style={{ backgroundColor: `rgb(${role.color.join(",")})` }}
                />
                <span className="text-white font-bold">{role.name}</span>
              </div>
              <p className="text-gray-400 text-sm mt-1 ml-7">
                {role.surface_identity}
              </p>
            </button>
          ))}
        </div>
        <button
          onClick={startGame}
          disabled={!selectedRole}
          className="w-full mt-6 py-3 rounded-lg bg-green-600 text-white text-lg font-bold hover:bg-green-500 disabled:opacity-50"
        >
          开始游戏
        </button>
      </div>
    );
  }

  const canChat =
    (phase === "discuss" || phase === "discuss2") && charId;
  const isInLobby = phase === "lobby";
  const isHost = playerId === host;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      {/* Left: Scene + Phase Info */}
      <div className="space-y-4">
        {/* Scene placeholder */}
        <div className="relative bg-gray-900 rounded-lg border border-gray-700 overflow-hidden" style={{ aspectRatio: "4/3" }}>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <p className="text-4xl mb-2">
                {phase === "lobby" && "🏮"}
                {phase === "role_select" && "🎭"}
                {(phase === "discuss" || phase === "discuss2") && "🏛️"}
                {phase === "investigate" && "🔍"}
                {phase === "vote" && "🗳️"}
                {phase === "reveal" && "⚡"}
                {(phase === "intro" || !phase) && "📜"}
              </p>
              <p className="text-gray-400">
                {phase === "lobby" && "等待玩家加入..."}
                {phase === "intro" && "故事即将开始"}
                {(phase === "discuss" || phase === "discuss2") && "自由讨论中"}
                {phase === "investigate" && "搜证阶段"}
                {phase === "vote" && "投票进行中"}
                {phase === "reveal" && "真相揭晓"}
              </p>
            </div>
          </div>
        </div>

        {/* Phase bar */}
        <div className="bg-gray-900 rounded-lg border border-gray-700 p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-white font-bold text-sm">
              {phase === "lobby" && "大厅"}
              {phase === "intro" && "开场"}
              {phase === "discuss" && "自由讨论"}
              {phase === "investigate" && "搜证阶段"}
              {phase === "discuss2" && "深入讨论"}
              {phase === "vote" && "最终投票"}
              {phase === "reveal" && "真相揭晓"}
            </span>
            <span className="text-xs text-gray-500">
              {mode === "solo" ? "单人模式" : "多人模式"}
            </span>
          </div>

          {/* Phase progress */}
          <div className="flex gap-1">
            {["intro", "discuss", "investigate", "discuss2", "vote", "reveal"].map(
              (p, i) => (
                <div
                  key={p}
                  className={`flex-1 h-1.5 rounded-full ${
                    ["intro", "discuss", "investigate", "discuss2", "vote", "reveal"].indexOf(phase) >= i
                      ? "bg-indigo-500"
                      : "bg-gray-700"
                  }`}
                />
              )
            )}
          </div>
        </div>

        {/* Players */}
        <div className="bg-gray-900 rounded-lg border border-gray-700 p-4">
          <h3 className="text-white font-bold text-sm mb-3">玩家</h3>
          <div className="space-y-2">
            {players.map((p) => (
              <div key={p.id} className="flex items-center gap-3">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{
                    backgroundColor: p.color
                      ? `rgb(${p.color.join(",")})`
                      : "#666",
                  }}
                />
                <span className="text-gray-300 text-sm">
                  {p.is_ai ? `AI·${p.char_id ? CHAR_NAMES[p.char_id] || "" : ""}` : p.name}
                </span>
                {p.char_id && (
                  <span className="text-gray-500 text-xs">
                    ({CHAR_NAMES[p.char_id] || p.char_id})
                  </span>
                )}
                {p.id === host && !p.is_ai && (
                  <span className="text-yellow-400 text-xs ml-auto">Host</span>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* My Role Card */}
        {charId && (
          <div className="bg-gray-900 rounded-lg border border-gray-700 p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div
                  className="w-4 h-4 rounded-full"
                  style={{ backgroundColor: `rgb(${charColor.join(",")})` }}
                />
                <span className="text-white font-bold">{charName}</span>
              </div>
              <button
                onClick={() => setShowScript(!showScript)}
                className="text-xs px-3 py-1 rounded bg-gray-700 text-gray-300 hover:bg-gray-600"
              >
                {showScript ? "隐藏剧本" : "查看剧本"}
              </button>
            </div>
            {showScript && (
              <pre className="mt-3 p-3 bg-gray-800 rounded text-gray-300 text-xs whitespace-pre-wrap max-h-48 overflow-y-auto">
                {privateScript}
              </pre>
            )}
          </div>
        )}
      </div>

      {/* Right: Chat + Actions */}
      <div className="space-y-4">
        {/* Chat messages */}
        <div className="bg-gray-900 rounded-lg border border-gray-700 p-4 flex flex-col" style={{ minHeight: "500px" }}>
          <div className="flex-1 overflow-y-auto space-y-3 mb-3 max-h-96">
            {messages.length === 0 && (
              <p className="text-gray-600 text-center text-sm mt-20">
                等待游戏开始...
              </p>
            )}
            {messages.map((msg, i) => (
              <div key={i}>
                {msg.type === "narration" && (
                  <div className="text-center">
                    <div className="inline-block px-4 py-2 bg-yellow-900/30 border border-yellow-700/50 rounded-lg">
                      <p className="text-yellow-200 text-sm italic">
                        {msg.text}
                      </p>
                    </div>
                  </div>
                )}
                {msg.type === "chat" && (
                  <div
                    className={`flex gap-2 ${
                      msg.player_id === playerId ? "justify-end" : "justify-start"
                    }`}
                  >
                    {msg.player_id !== playerId && msg.color && (
                      <div
                        className="w-6 h-6 rounded-full flex-shrink-0 mt-1"
                        style={{ backgroundColor: `rgb(${msg.color.join(",")})` }}
                      />
                    )}
                    <div
                      className={`max-w-[80%] rounded-lg px-3 py-2 ${
                        msg.player_id === playerId
                          ? "bg-indigo-600/30 border border-indigo-500/30"
                          : "bg-gray-800 border border-gray-700"
                      }`}
                    >
                      <p className="text-xs text-gray-400 mb-0.5">
                        {msg.char_name}
                        {msg.is_ai && " (AI)"}
                      </p>
                      <p className="text-gray-200 text-sm">{msg.message}</p>
                    </div>
                  </div>
                )}
                {msg.type === "clue" && msg.clue && (
                  <div className="px-3 py-2 bg-amber-900/20 border border-amber-700/40 rounded-lg">
                    <p className="text-amber-300 text-sm font-bold">
                      🔍 {msg.clue.name}
                    </p>
                    <p className="text-gray-300 text-sm mt-1">
                      {msg.clue.description}
                    </p>
                    <p className="text-gray-500 text-xs mt-1 italic">
                      推理：{msg.clue.inference}
                    </p>
                  </div>
                )}
                {msg.type === "phase" && (
                  <div className="text-center">
                    <p className="text-indigo-400 text-sm">—— {msg.description} ——</p>
                  </div>
                )}
                {msg.type === "truth" && (
                  <div className="px-4 py-3 bg-red-900/20 border border-red-700/40 rounded-lg">
                    <p className="text-red-300 text-sm font-bold mb-1">
                      ⚡ 真相揭晓
                    </p>
                    <p className="text-gray-200 text-sm whitespace-pre-wrap">
                      {msg.text}
                    </p>
                  </div>
                )}
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>

          {/* Chat input */}
          {canChat && (
            <div className="flex gap-2">
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                placeholder={`以${charName}的身份发言...`}
                maxLength={500}
                className="flex-1 px-3 py-2 rounded bg-gray-800 border border-gray-600 text-white text-sm"
              />
              <button
                onClick={sendMessage}
                className="px-4 py-2 rounded bg-indigo-600 text-white text-sm font-bold hover:bg-indigo-500"
              >
                发送
              </button>
            </div>
          )}

          {/* Phase actions */}
          {canChat && isHost && (
            <button
              onClick={endDiscuss}
              className="w-full mt-2 py-2 rounded bg-amber-600 text-white text-sm font-bold hover:bg-amber-500"
            >
              {phase === "discuss" ? "结束讨论，进入搜证" : "结束讨论，进入投票"}
            </button>
          )}
        </div>

        {/* Voting panel */}
        {phase === "investigate" && (
          <div className="bg-gray-900 rounded-lg border border-gray-700 p-4">
            <h3 className="text-white font-bold text-sm mb-3">搜证投票</h3>
            <p className="text-gray-400 text-xs mb-3">选择要搜查的宿舍和随身物品</p>
            <div className="grid grid-cols-2 gap-2">
              {Object.entries(CHAR_NAMES).map(([id, name]) => (
                <button
                  key={id}
                  onClick={() => sendVote("dorm_vote", id)}
                  className={`px-3 py-2 rounded border text-sm font-bold ${
                    votes["dorm_vote"] === id
                      ? "bg-indigo-600 border-indigo-500 text-white"
                      : "bg-gray-800 border-gray-600 text-gray-400 hover:bg-gray-700"
                  }`}
                >
                  搜查{name}宿舍
                </button>
              ))}
            </div>
            <div className="grid grid-cols-2 gap-2 mt-2">
              {Object.entries(CHAR_NAMES).map(([id, name]) => (
                <button
                  key={id}
                  onClick={() => sendVote("body_vote", id)}
                  className={`px-3 py-2 rounded border text-sm font-bold ${
                    votes["body_vote"] === id
                      ? "bg-green-600 border-green-500 text-white"
                      : "bg-gray-800 border-gray-600 text-gray-400 hover:bg-gray-700"
                  }`}
                >
                  搜查{name}身上
                </button>
              ))}
            </div>
          </div>
        )}

        {phase === "vote" && (
          <div className="bg-gray-900 rounded-lg border border-gray-700 p-4">
            <h3 className="text-white font-bold text-sm mb-3">
              最终投票 — 指认鱼妖
            </h3>
            <div className="space-y-2">
              {Object.entries(CHAR_NAMES).map(([id, name]) => (
                <button
                  key={id}
                  onClick={() => sendVote("accuse", id)}
                  className={`w-full text-left px-4 py-3 rounded-lg border text-sm font-bold ${
                    votes["accuse"] === id
                      ? "bg-red-600 border-red-500 text-white"
                      : "bg-gray-800 border-gray-600 text-gray-400 hover:bg-gray-700"
                  }`}
                >
                  指认 {name}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Lobby start button */}
        {isInLobby && isHost && (
          <button
            onClick={startGame}
            className="w-full py-3 rounded-lg bg-green-600 text-white text-lg font-bold hover:bg-green-500"
          >
            {mode === "solo" ? "选择角色并开始" : "开始游戏"}
          </button>
        )}

        {error && <p className="text-red-400 text-sm">{error}</p>}
      </div>
    </div>
  );
}

const CHAR_NAMES: Record<string, string> = {
  hunter: "除妖人",
  maid: "丫鬟",
  swordsman: "剑客",
  cook: "女厨",
};

export default function MysteryGamePage() {
  return (
    <Suspense>
      <MysteryGameContent />
    </Suspense>
  );
}
