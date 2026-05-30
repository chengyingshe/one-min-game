"use client";

import { Suspense, useState } from "react";
import { useRouter } from "next/navigation";
import { createMysteryRoom } from "@/lib/api";

function MysteryEntryContent() {
  const router = useRouter();

  const [roomCode, setRoomCode] = useState("");
  const [mode, setMode] = useState<"solo" | "multi">("solo");
  const [hostName, setHostName] = useState("");
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState("");

  const handleJoin = () => {
    const code = roomCode.trim().toUpperCase();
    if (code.length < 4) {
      setError("Enter a valid room code");
      return;
    }
    router.push(`/mystery/${code}`);
  };

  const handleCreate = async () => {
    setCreating(true);
    setError("");
    try {
      const room = await createMysteryRoom(
        mode,
        hostName.trim() || "Host",
        mode === "solo" ? 1 : 4
      );
      router.push(`/mystery/${room.room_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create room");
      setCreating(false);
    }
  };

  return (
    <div className="max-w-lg mx-auto py-12 px-4">
      <h1 className="text-3xl font-bold text-white mb-2 text-center">
        相府鱼美人
      </h1>
      <p className="text-gray-400 text-center mb-8">
        剧本杀 — 多人在线推理游戏
      </p>

      {/* Mode selection */}
      <div className="bg-gray-900 rounded-lg border border-gray-700 p-6 mb-6">
        <h2 className="text-lg font-bold text-white mb-4">游戏模式</h2>
        <div className="flex gap-3">
          <button
            onClick={() => setMode("solo")}
            className={`flex-1 py-3 rounded-lg border text-sm font-bold ${
              mode === "solo"
                ? "bg-indigo-600 border-indigo-500 text-white"
                : "bg-gray-800 border-gray-600 text-gray-400 hover:bg-gray-700"
            }`}
          >
            单人 + AI
          </button>
          <button
            onClick={() => setMode("multi")}
            className={`flex-1 py-3 rounded-lg border text-sm font-bold ${
              mode === "multi"
                ? "bg-indigo-600 border-indigo-500 text-white"
                : "bg-gray-800 border-gray-600 text-gray-400 hover:bg-gray-700"
            }`}
          >
            多人在线
          </button>
        </div>
        <p className="text-gray-500 text-xs mt-2 text-center">
          {mode === "solo"
            ? "你扮演一个角色，AI 扮演其余角色"
            : "邀请朋友一起玩，每人扮演一个角色"}
        </p>
      </div>

      {/* Create room */}
      <div className="bg-gray-900 rounded-lg border border-gray-700 p-6 mb-6">
        <h2 className="text-lg font-bold text-white mb-4">创建房间</h2>
        <input
          type="text"
          value={hostName}
          onChange={(e) => setHostName(e.target.value)}
          placeholder="你的名字"
          maxLength={20}
          className="w-full px-4 py-2 rounded bg-gray-800 border border-gray-600 text-white mb-3"
        />
        <button
          onClick={handleCreate}
          disabled={creating}
          className="w-full py-2 rounded-lg bg-green-600 text-white font-bold hover:bg-green-500 disabled:opacity-50"
        >
          {creating ? "Creating..." : "创建房间"}
        </button>
      </div>

      {/* Join room */}
      <div className="bg-gray-900 rounded-lg border border-gray-700 p-6">
        <h2 className="text-lg font-bold text-white mb-4">加入房间</h2>
        <input
          type="text"
          value={roomCode}
          onChange={(e) => setRoomCode(e.target.value.toUpperCase())}
          onKeyDown={(e) => e.key === "Enter" && handleJoin()}
          placeholder="输入房间号"
          maxLength={6}
          className="w-full px-4 py-2 rounded bg-gray-800 border border-gray-600 text-white mb-3 text-center font-mono text-lg tracking-widest"
        />
        <button
          onClick={handleJoin}
          className="w-full py-2 rounded-lg bg-indigo-600 text-white font-bold hover:bg-indigo-500"
        >
          加入房间
        </button>
      </div>

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

export default function MysteryEntryPage() {
  return (
    <Suspense>
      <MysteryEntryContent />
    </Suspense>
  );
}
