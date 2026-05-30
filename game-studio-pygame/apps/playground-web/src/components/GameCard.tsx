import type { Game } from "@/lib/types";
import { screenshotUrl } from "@/lib/api";

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
  return (
    <a
      href={`/play/${game.name}`}
      className="group block rounded-lg border border-gray-700 bg-gray-800 overflow-hidden transition-colors hover:border-indigo-500 hover:bg-gray-750"
    >
      <div className="aspect-[4/3] bg-gray-900 flex items-center justify-center overflow-hidden">
        {game.preview_image_url ? (
          <img
            src={screenshotUrl(game.preview_image_url)}
            alt={game.display_name}
            className="w-full h-full object-cover"
          />
        ) : (
          <span className="text-4xl text-gray-600">🎮</span>
        )}
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
