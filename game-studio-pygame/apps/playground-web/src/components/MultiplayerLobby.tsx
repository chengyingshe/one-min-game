"use client";

import { useEffect, useRef, useState, useCallback } from "react";

interface LobbyPlayer {
  id: string;
  name: string;
  color: number[];
}

interface Props {
  roomId: string;
  wsUrl: string;
  onGameStart: (
    ws: WebSocket,
    playerId: string,
    players: LobbyPlayer[],
  ) => void;
}

export default function MultiplayerLobby({
  roomId,
  wsUrl,
  onGameStart,
}: Props) {
  const wsRef = useRef<WebSocket | null>(null);
  const [players, setPlayers] = useState<LobbyPlayer[]>([]);
  const [playerId, setPlayerId] = useState("");
  const [playerColor, setPlayerColor] = useState<number[]>([255, 255, 255]);
  const [name, setName] = useState("");
  const [joined, setJoined] = useState(false);
  const [error, setError] = useState("");
  const [host, setHost] = useState("");
  const [maxPlayers, setMaxPlayers] = useState(4);

  const connect = useCallback(() => {
    if (!name.trim()) {
      setError("Enter your name");
      return;
    }

    setError("");
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      ws.send(JSON.stringify({ type: "join", name: name.trim() }));
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        switch (msg.type) {
          case "lobby":
            setPlayers(msg.players || []);
            setHost(msg.host || "");
            if (msg.max_players) setMaxPlayers(msg.max_players);
            break;
          case "joined":
            setPlayerId(msg.player_id);
            setPlayerColor(msg.color || [255, 255, 255]);
            setJoined(true);
            break;
          case "game_start":
            onGameStart(ws, msg.player_id || playerId, msg.players || players);
            break;
          case "error":
            setError(msg.message || "Error");
            break;
        }
      } catch {}
    };

    ws.onerror = () => setError("Connection failed");
    ws.onclose = () => {
      if (!joined) setError("Disconnected");
    };
  }, [wsUrl, name, joined, playerId, players, onGameStart]);

  const startGame = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "start_game" }));
    }
  }, []);

  useEffect(() => {
    return () => {
      wsRef.current?.close();
    };
  }, []);

  if (!joined) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] bg-gray-900 rounded-lg border border-gray-700 p-8">
        <h2 className="text-2xl font-bold text-white mb-2">Join Room</h2>
        <p className="text-gray-400 mb-6">
          Room:{" "}
          <span className="font-mono text-indigo-400 text-lg">{roomId}</span>
        </p>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && connect()}
          placeholder="Your name"
          maxLength={20}
          className="px-4 py-2 rounded bg-gray-800 border border-gray-600 text-white mb-4 w-64 text-center"
        />
        <button
          onClick={connect}
          className="px-6 py-2 rounded-lg bg-indigo-600 text-white font-bold hover:bg-indigo-500"
        >
          Join
        </button>
        {error && <p className="text-red-400 text-sm mt-2">{error}</p>}
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] bg-gray-900 rounded-lg border border-gray-700 p-8">
      <h2 className="text-2xl font-bold text-white mb-1">Lobby</h2>
      <p className="text-gray-400 mb-6">
        Room code:{" "}
        <span className="font-mono text-indigo-400 text-xl tracking-widest">
          {roomId}
        </span>
      </p>

      <div className="space-y-2 mb-6 w-full max-w-xs">
        {players.map((p) => (
          <div
            key={p.id}
            className="flex items-center gap-3 px-4 py-2 rounded bg-gray-800"
          >
            <div
              className="w-4 h-4 rounded-full"
              style={{ backgroundColor: `rgb(${p.color.join(",")})` }}
            />
            <span className="text-white">{p.name}</span>
            {p.id === host && (
              <span className="text-xs text-yellow-400 ml-auto">Host</span>
            )}
          </div>
        ))}
        <p className="text-gray-500 text-xs text-center mt-2">
          {players.length} / {maxPlayers} players
        </p>
      </div>

      {playerId === host ? (
        <button
          onClick={startGame}
          disabled={players.length < 1}
          className="px-8 py-3 rounded-lg bg-green-600 text-white text-lg font-bold hover:bg-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Start Game
        </button>
      ) : (
        <p className="text-gray-400 text-sm">Waiting for host to start...</p>
      )}

      {error && <p className="text-red-400 text-sm mt-2">{error}</p>}
    </div>
  );
}
