import type { Game } from "@/lib/types";

const GENRE_ICONS: Record<string, { emoji: string; bg: string }> = {
  shooter: { emoji: "🔫", bg: "bg-red-950" },
  platformer: { emoji: "🏃", bg: "bg-green-950" },
  flappy: { emoji: "🐦", bg: "bg-sky-950" },
  topdown: { emoji: "⚔️", bg: "bg-amber-950" },
  rogue: { emoji: "🗡️", bg: "bg-purple-950" },
  arcade: { emoji: "🕹️", bg: "bg-blue-950" },
  puzzle: { emoji: "🧩", bg: "bg-pink-950" },
  fps: { emoji: "🎯", bg: "bg-orange-950" },
};

const DEFAULT_ICON = { emoji: "🎮", bg: "bg-gray-900" };

function StarRating({ rating, count }: { rating: number; count: number }) {
  const full = Math.round(rating);
  return (
    <span className="flex items-center gap-1 text-sm">
      <span className="text-yellow-500">
        {"★".repeat(full)}
        {"☆".repeat(5 - full)}
      </span>
      {count > 0 && <span className="text-gray-400">({count})</span>}
    </span>
  );
}

export default function GameCard({ game }: { game: Game }) {
  const icon = GENRE_ICONS[game.genre] ?? DEFAULT_ICON;

  return (
    <a
      href={`/play/${game.name}`}
      className="group block rounded-lg border border-gray-700 bg-gray-800 overflow-hidden transition-colors hover:border-indigo-500 hover:bg-gray-750"
    >
      <div
        className={`aspect-[4/3] ${icon.bg} flex items-center justify-center overflow-hidden`}
      >
        <span className="text-6xl">{icon.emoji}</span>
      </div>
      <div className="p-3 space-y-1">
        <h3 className="font-semibold text-white truncate group-hover:text-indigo-400">
          {game.display_name}
        </h3>
        <div className="flex items-center justify-between">
          <span className="inline-block text-xs px-2 py-0.5 rounded bg-indigo-900 text-indigo-300">
            {game.genre}
          </span>
          <StarRating rating={game.avg_rating} count={game.rating_count} />
        </div>
        <p className="text-xs text-gray-400">
          {game.play_count} play{game.play_count !== 1 ? "s" : ""}
        </p>
      </div>
    </a>
  );
}
