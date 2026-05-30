"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { NPC, MemoryEntry } from "@/lib/types";
import MemoryCard from "@/components/MemoryCard";
import LoadingSpinner from "@/components/LoadingSpinner";

export const dynamic = "force-dynamic";

export default function MemoriesPage() {
  const router = useRouter();
  const [npcs, setNpcs] = useState<NPC[]>([]);
  const [selectedNpc, setSelectedNpc] = useState<NPC | null>(null);
  const [memories, setMemories] = useState<MemoryEntry[]>([]);
  const [tier, setTier] = useState("all");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .listNpcs()
      .then((data) => {
        setNpcs(data);
        if (data.length > 0) setSelectedNpc(data[0]);
      })
      .catch((e) => setError((e as Error).message));
  }, []);

  useEffect(() => {
    if (!selectedNpc) return;
    async function loadMemories() {
      setLoading(true);
      try {
        const data = await api.getMemoryTimeline(selectedNpc!.id);
        setMemories(data.memories || []);
      } catch (e: unknown) {
        setError((e as Error).message);
      } finally {
        setLoading(false);
      }
    }
    loadMemories();
  }, [selectedNpc]);

  const filteredMemories =
    tier === "all" ? memories : memories.filter((m) => m.tier === tier);

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="font-display text-2xl">📜 记忆回溯</h1>
        <button
          onClick={() => router.push("/town")}
          className="chinese-btn text-sm"
        >
          ← 返回小镇
        </button>
      </div>

      {/* NPC Selector */}
      <div className="flex gap-2">
        {npcs.map((npc) => (
          <button
            key={npc.id}
            onClick={() => {
              setSelectedNpc(npc);
              setTier("all");
            }}
            className={`rounded-full px-4 py-1.5 text-sm transition-colors ${
              selectedNpc?.id === npc.id
                ? "bg-chinese-red text-white"
                : "bg-amber-100 hover:bg-amber-200"
            }`}
          >
            {npc.avatar_emoji} {npc.name}
          </button>
        ))}
      </div>

      {/* Tier Filter */}
      <div className="flex gap-2">
        {[
          { key: "all", label: "全部" },
          { key: "short_term", label: "🕐 近期" },
          { key: "medium_term", label: "📝 印象" },
          { key: "long_term", label: "💎 重要" },
        ].map((t) => (
          <button
            key={t.key}
            onClick={() => setTier(t.key)}
            className={`rounded-full px-3 py-1 text-xs transition-colors ${
              tier === t.key
                ? "bg-ink-black text-white"
                : "bg-stone-100 hover:bg-stone-200"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Memory Cards */}
      {loading ? (
        <div className="flex justify-center py-8">
          <LoadingSpinner text="加载记忆中..." />
        </div>
      ) : filteredMemories.length > 0 ? (
        <div className="space-y-2">
          {filteredMemories.map((m, i) => (
            <MemoryCard key={m.id || i} memory={m} />
          ))}
        </div>
      ) : (
        <div className="py-12 text-center text-stone-400">
          <p className="text-4xl">📭</p>
          <p className="mt-2">暂无记忆</p>
        </div>
      )}

      {error && <p className="text-center text-sm text-red-500">{error}</p>}
    </div>
  );
}
