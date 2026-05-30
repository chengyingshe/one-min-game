"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import GameCard from "@/components/GameCard";
import { listGames } from "@/lib/api";
import type { Game, Genre } from "@/lib/types";
import { GENRES } from "@/lib/types";

const SORT_OPTIONS = [
  { value: "created_at", label: "Newest" },
  { value: "play_count", label: "Most Played" },
  { value: "avg_rating", label: "Top Rated" },
] as const;

export default function GalleryPage() {
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [genre, setGenre] = useState<string>("");
  const [sort, setSort] = useState<string>("created_at");
  const [search, setSearch] = useState("");

  useEffect(() => {
    setLoading(true);
    setError("");
    listGames({
      genre: genre || undefined,
      sort,
      order: "desc",
      search: search || undefined,
    })
      .then(setGames)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [genre, sort, search]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 justify-between">
        <h1 className="text-2xl font-bold">Game Gallery</h1>
        <input
          type="text"
          placeholder="Search games..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full sm:w-64 rounded bg-gray-800 border border-gray-600 px-3 py-2 text-sm text-white focus:border-indigo-500 focus:outline-none"
        />
      </div>

      <div className="flex flex-wrap gap-2 items-center">
        <span className="text-sm text-gray-400 mr-1">Genre:</span>
        <button
          onClick={() => setGenre("")}
          className={`px-3 py-1 text-sm rounded ${genre === "" ? "bg-indigo-600 text-white" : "bg-gray-700 text-gray-300 hover:bg-gray-600"}`}
        >
          All
        </button>
        {GENRES.map((g) => (
          <button
            key={g}
            onClick={() => setGenre(g)}
            className={`px-3 py-1 text-sm rounded capitalize ${genre === g ? "bg-indigo-600 text-white" : "bg-gray-700 text-gray-300 hover:bg-gray-600"}`}
          >
            {g}
          </button>
        ))}

        <span className="text-sm text-gray-400 ml-4 mr-1">Sort:</span>
        {SORT_OPTIONS.map((opt) => (
          <button
            key={opt.value}
            onClick={() => setSort(opt.value)}
            className={`px-3 py-1 text-sm rounded ${sort === opt.value ? "bg-indigo-600 text-white" : "bg-gray-700 text-gray-300 hover:bg-gray-600"}`}
          >
            {opt.label}
          </button>
        ))}
      </div>

      {loading && <p className="text-gray-400">Loading games...</p>}
      {error && <p className="text-red-400">{error}</p>}

      {!loading && games.length === 0 && (
        <p className="text-gray-500">
          No games found. Be the first to upload one!
        </p>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <Link href="/mystery" className="group block rounded-lg border border-amber-700/50 bg-gradient-to-br from-gray-800 to-gray-900 p-5 hover:border-amber-500 hover:shadow-lg hover:shadow-amber-900/20 transition-all">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-2xl">🏮</span>
            <h3 className="text-lg font-bold text-amber-200">相府鱼美人</h3>
            <span className="ml-auto text-xs bg-amber-900/50 text-amber-300 px-2 py-0.5 rounded">剧本杀</span>
          </div>
          <p className="text-gray-400 text-sm mb-3">多人在线推理游戏 — LLM 主持人法海主持，AI 角色扮演，搜证推理指认鱼妖</p>
          <div className="flex gap-2">
            <span className="text-xs bg-gray-700 text-gray-300 px-2 py-0.5 rounded">单人+AI</span>
            <span className="text-xs bg-gray-700 text-gray-300 px-2 py-0.5 rounded">多人在线</span>
          </div>
        </Link>

        {games.map((game) => (
          <GameCard key={game.id} game={game} />
        ))}
      </div>
    </div>
  );
}
