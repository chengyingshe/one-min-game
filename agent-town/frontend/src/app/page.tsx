"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { IDENTITIES } from "@/lib/constants";
import CharacterPortrait from "@/components/CharacterPortrait";

export const dynamic = "force-dynamic";

export default function HomePage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [identity, setIdentity] = useState(IDENTITIES[0]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [seeded, setSeeded] = useState(false);

  async function handleSeed() {
    try {
      setLoading(true);
      setError("");
      await api.seed();
      setSeeded(true);
    } catch (e) {
      setError("初始化失败，请检查后端是否已启动");
    } finally {
      setLoading(false);
    }
  }

  async function handleEnter() {
    if (!name.trim()) {
      setError("请输入你的名字");
      return;
    }
    try {
      setLoading(true);
      setError("");
      const player = await api.createPlayer(name.trim(), identity);
      localStorage.setItem("player_id", String(player.id));
      localStorage.setItem("player_name", player.name);
      router.push("/town");
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "创建角色失败";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col items-center justify-center py-12">
      {/* Title */}
      <div className="mb-12 text-center">
        <div className="mb-2 text-6xl">🏮</div>
        <h1 className="font-display text-4xl tracking-widest text-ink-black">
          时空杂货镇
        </h1>
        <p className="mt-3 text-stone-500">
          与经典文学人物相遇，展开一段奇妙旅程
        </p>
      </div>

      {/* Characters Preview */}
      <div className="mb-10 flex gap-6 text-center">
        {[
          { name: "林黛玉", source: "红楼梦", emoji: "🌸" },
          { name: "孙悟空", source: "西游记", emoji: "🐵" },
          { name: "张飞", source: "三国演义", emoji: "💪" },
        ].map((char) => (
          <div key={char.name} className="flex flex-col items-center">
            <CharacterPortrait
              characterName={char.name}
              size="md"
              fallbackEmoji={char.emoji}
            />
            <span className="mt-1 font-display text-sm">{char.name}</span>
            <span className="text-xs text-stone-400">《{char.source}》</span>
          </div>
        ))}
      </div>

      {/* Seed Button */}
      {!seeded && (
        <button
          onClick={handleSeed}
          disabled={loading}
          className="chinese-btn mb-6 text-sm"
        >
          {loading ? "初始化中..." : "🏗️ 初始化游戏数据"}
        </button>
      )}

      {/* Create Player Form */}
      <div className="chinese-card w-full max-w-sm">
        <h2 className="mb-4 text-center font-display text-lg">创建你的角色</h2>

        <div className="mb-4">
          <label className="mb-1 block text-sm text-stone-600">你的名字</label>
          <input
            type="text"
            className="chinese-input"
            placeholder="请输入名字..."
            value={name}
            onChange={(e) => setName(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleEnter()}
          />
        </div>

        <div className="mb-6">
          <label className="mb-2 block text-sm text-stone-600">选择身份</label>
          <div className="flex flex-wrap gap-2">
            {IDENTITIES.map((id) => (
              <button
                key={id}
                onClick={() => setIdentity(id)}
                className={`rounded-full px-3 py-1 text-sm transition-colors ${
                  identity === id
                    ? "bg-chinese-red text-white"
                    : "bg-amber-100 text-stone-600 hover:bg-amber-200"
                }`}
              >
                {id}
              </button>
            ))}
          </div>
        </div>

        {error && (
          <p className="mb-3 text-center text-sm text-red-500">{error}</p>
        )}

        <button
          onClick={handleEnter}
          disabled={loading || !name.trim()}
          className="chinese-btn-primary w-full text-lg"
        >
          {loading ? "进入中..." : "🚶 进入小镇"}
        </button>
      </div>
    </div>
  );
}
