"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { GameState, Player } from "@/lib/types";
import WorldClock from "@/components/WorldClock";
import TownMap from "@/components/TownMap";
import ConversationFeed, {
  DialogueBubbleOverlay,
} from "@/components/ConversationFeed";
import { useGameWebSocket } from "@/hooks/useGameWebSocket";

export const dynamic = "force-dynamic";

export default function TownPage() {
  const router = useRouter();
  const [player, setPlayer] = useState<Player | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const {
    positions,
    conversations,
    currentDay,
    currentTime,
    paused,
    connected,
    sendMessage,
  } = useGameWebSocket();

  // Load player data
  useEffect(() => {
    async function load() {
      try {
        const pid = localStorage.getItem("player_id");
        if (pid) {
          const p = await api.getPlayer(Number(pid));
          setPlayer(p);
        }
      } catch {
        // Player might not exist yet
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  function handleNpcClick(npcId: number) {
    if (!player) {
      setError("请先创建角色");
      return;
    }
    router.push(`/dialogue?npc_id=${npcId}`);
  }

  function handleTogglePause() {
    sendMessage({ action: paused ? "resume" : "pause" });
  }

  function handleSpeed(speed: number) {
    sendMessage({ action: "set_speed", interval: speed });
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="flex gap-1">
          <span className="inline-block h-3 w-3 animate-bounce rounded-full bg-amber-400" />
          <span className="inline-block h-3 w-3 animate-bounce rounded-full bg-amber-400 [animation-delay:150ms]" />
          <span className="inline-block h-3 w-3 animate-bounce rounded-full bg-amber-400 [animation-delay:300ms]" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="font-display text-2xl">🏮 小镇地图</h1>
        <div className="flex items-center gap-3">
          <WorldClock day={currentDay} time={currentTime} />
          {/* Connection status */}
          <span
            className={`h-2.5 w-2.5 rounded-full ${connected ? "bg-green-500" : "bg-red-400"}`}
            title={connected ? "已连接" : "未连接"}
          />
        </div>
      </div>

      {/* Simulation controls */}
      <div className="flex items-center gap-2">
        <button onClick={handleTogglePause} className="chinese-btn text-sm">
          {paused ? "▶ 继续" : "⏸ 暂停"}
        </button>
        <span className="text-xs text-stone-400">速度:</span>
        <button
          onClick={() => handleSpeed(5)}
          className="chinese-btn text-xs px-2 py-1"
        >
          1x
        </button>
        <button
          onClick={() => handleSpeed(3)}
          className="chinese-btn text-xs px-2 py-1"
        >
          2x
        </button>
        <button
          onClick={() => handleSpeed(1)}
          className="chinese-btn text-xs px-2 py-1"
        >
          4x
        </button>
      </div>

      {/* Player info */}
      {player && (
        <div className="chinese-card flex items-center gap-3">
          <span className="text-3xl">🧑</span>
          <div>
            <span className="font-display">{player.name}</span>
            <span className="ml-2 text-xs text-stone-400">
              （{player.identity}）
            </span>
          </div>
          <div className="ml-auto text-sm text-stone-500">
            💰 {player.wealth} 金币
          </div>
        </div>
      )}

      {/* Map with characters */}
      <div className="relative">
        <TownMap positions={positions} onNpcClick={handleNpcClick} />
        <DialogueBubbleOverlay conversations={conversations} />
      </div>

      {/* NPC conversation feed */}
      <ConversationFeed conversations={conversations} />

      {/* NPC quick access cards */}
      <div>
        <h2 className="mb-3 font-display text-lg">角色一览</h2>
        <div className="grid gap-3 sm:grid-cols-3">
          {positions.map((npc) => (
            <div
              key={npc.id}
              className="chinese-card flex cursor-pointer items-center gap-2"
              onClick={() => handleNpcClick(npc.id)}
            >
              <span className="text-2xl">{npc.avatar_emoji || "👤"}</span>
              <div>
                <div className="font-display text-sm">{npc.name}</div>
                <div className="text-xs text-stone-400">
                  {npc.current_location}
                  {npc.is_moving && " (移动中...)"}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {error && <p className="text-center text-sm text-red-500">{error}</p>}
    </div>
  );
}
