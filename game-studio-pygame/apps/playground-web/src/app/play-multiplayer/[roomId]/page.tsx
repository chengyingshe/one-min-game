"use client";

import { useState, useCallback } from "react";
import { useParams } from "next/navigation";
import MultiplayerLobby from "@/components/MultiplayerLobby";
import MultiplayerPlayer from "@/components/MultiplayerPlayer";
import { getWsMultiplayerUrl } from "@/lib/api";

type Phase = "lobby" | "playing";

interface PlayerInfo {
  id: string;
  name: string;
  color: number[];
}

export default function MultiplayerPlayPage() {
  const params = useParams();
  const roomId = params.roomId as string;
  const wsUrl = getWsMultiplayerUrl(roomId);

  const [phase, setPhase] = useState<Phase>("lobby");
  const [gameWs, setGameWs] = useState<WebSocket | null>(null);
  const [playerId, setPlayerId] = useState("");
  const [playerColor, setPlayerColor] = useState<number[]>([255, 255, 255]);
  const [players, setPlayers] = useState<PlayerInfo[]>([]);

  const handleGameStart = useCallback(
    (ws: WebSocket, pid: string, plist: PlayerInfo[]) => {
      setGameWs(ws);
      setPlayerId(pid);
      setPlayers(plist);
      const me = plist.find((p) => p.id === pid);
      if (me) setPlayerColor(me.color);
      setPhase("playing");
    },
    [],
  );

  const handleQuit = useCallback(() => {
    if (gameWs) {
      gameWs.close();
      setGameWs(null);
    }
    setPhase("lobby");
  }, [gameWs]);

  return (
    <div className="max-w-4xl mx-auto py-6 px-4">
      <a href="/" className="text-sm text-indigo-400 hover:text-indigo-300">
        &larr; Back to Gallery
      </a>

      <div className="mt-4">
        {phase === "lobby" && (
          <MultiplayerLobby
            roomId={roomId}
            wsUrl={wsUrl}
            onGameStart={handleGameStart}
          />
        )}
        {phase === "playing" && gameWs && (
          <MultiplayerPlayer
            ws={gameWs}
            playerId={playerId}
            playerColor={playerColor}
            players={players}
            onQuit={handleQuit}
          />
        )}
      </div>
    </div>
  );
}
