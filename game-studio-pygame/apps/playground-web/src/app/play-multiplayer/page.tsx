"use client";

import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { createRoom } from "@/lib/api";

function MultiplayerEntryContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const gameName = searchParams.get("game") || "";

  const [roomCode, setRoomCode] = useState("");
  const [hostName, setHostName] = useState("");
  const [maxPlayers, setMaxPlayers] = useState(4);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState("");

  const handleJoin = () => {
    const code = roomCode.trim().toUpperCase();
    if (code.length < 4) {
      setError("Enter a valid room code");
      return;
    }
    router.push(`/play-multiplayer/${code}`);
  };

  const handleCreate = async () => {
    if (!gameName) {
      setError(
        "No game specified. Go to a game page and click 'Play Multiplayer'",
      );
      return;
    }
    setCreating(true);
    setError("");
    try {
      const room = await createRoom(
        gameName,
        hostName.trim() || "Host",
        maxPlayers,
      );
      router.push(`/play-multiplayer/${room.room_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create room");
      setCreating(false);
    }
  };

  return (
    <div className="max-w-md mx-auto py-12 px-4">
      <h1 className="text-3xl font-bold text-white mb-8 text-center">
        Multiplayer
      </h1>

      {/* Join existing room */}
      <div className="bg-gray-900 rounded-lg border border-gray-700 p-6 mb-6">
        <h2 className="text-lg font-bold text-white mb-4">Join a Room</h2>
        <input
          type="text"
          value={roomCode}
          onChange={(e) => setRoomCode(e.target.value.toUpperCase())}
          onKeyDown={(e) => e.key === "Enter" && handleJoin()}
          placeholder="Enter room code (e.g. A3F7K9)"
          maxLength={6}
          className="w-full px-4 py-2 rounded bg-gray-800 border border-gray-600 text-white mb-3 text-center font-mono text-lg tracking-widest"
        />
        <button
          onClick={handleJoin}
          className="w-full py-2 rounded-lg bg-indigo-600 text-white font-bold hover:bg-indigo-500"
        >
          Join Room
        </button>
      </div>

      {/* Create new room */}
      {gameName && (
        <div className="bg-gray-900 rounded-lg border border-gray-700 p-6">
          <h2 className="text-lg font-bold text-white mb-4">Create a Room</h2>
          <p className="text-gray-400 text-sm mb-3">
            Game: <span className="text-white">{gameName}</span>
          </p>
          <input
            type="text"
            value={hostName}
            onChange={(e) => setHostName(e.target.value)}
            placeholder="Your name"
            maxLength={20}
            className="w-full px-4 py-2 rounded bg-gray-800 border border-gray-600 text-white mb-3"
          />
          <div className="mb-3">
            <p className="text-gray-400 text-sm mb-2">Max Players</p>
            <div className="flex gap-2">
              {[2, 3, 4].map((n) => (
                <button
                  key={n}
                  onClick={() => setMaxPlayers(n)}
                  className={`flex-1 py-1.5 rounded text-sm font-bold border ${
                    maxPlayers === n
                      ? "bg-indigo-600 border-indigo-500 text-white"
                      : "bg-gray-800 border-gray-600 text-gray-400 hover:bg-gray-700"
                  }`}
                >
                  {n}
                </button>
              ))}
            </div>
          </div>
          <button
            onClick={handleCreate}
            disabled={creating}
            className="w-full py-2 rounded-lg bg-green-600 text-white font-bold hover:bg-green-500 disabled:opacity-50"
          >
            {creating ? "Creating..." : "Create Room"}
          </button>
        </div>
      )}

      {error && (
        <p className="text-red-400 text-sm mt-4 text-center">{error}</p>
      )}

      <a
        href="/"
        className="block text-sm text-indigo-400 hover:text-indigo-300 text-center mt-6"
      >
        &larr; Back to Gallery
      </a>
    </div>
  );
}

export default function MultiplayerEntryPage() {
  return (
    <Suspense>
      <MultiplayerEntryContent />
    </Suspense>
  );
}
