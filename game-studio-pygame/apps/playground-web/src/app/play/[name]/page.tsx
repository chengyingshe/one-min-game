"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import ScreenshotViewer from "@/components/ScreenshotViewer";
import GamePlayer from "@/components/GamePlayer";
import {
  getGame,
  runGame,
  rateGame,
  incrementPlay,
  screenshotUrl,
  getWsPlayUrl,
} from "@/lib/api";
import type { Game, RunResult } from "@/lib/types";

function StarRatingInput({
  value,
  onChange,
}: {
  value: number;
  onChange: (r: number) => void;
}) {
  return (
    <div className="flex gap-1">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          onClick={() => onChange(star)}
          className={`text-2xl ${star <= value ? "text-yellow-400" : "text-gray-600"} hover:text-yellow-300`}
        >
          ★
        </button>
      ))}
    </div>
  );
}

export default function GameDetailPage() {
  const params = useParams();
  const name = params.name as string;

  const [game, setGame] = useState<Game | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [runResult, setRunResult] = useState<RunResult | null>(null);
  const [running, setRunning] = useState(false);
  const [userRating, setUserRating] = useState(0);
  const [ratingSaved, setRatingSaved] = useState(false);

  useEffect(() => {
    getGame(name)
      .then(setGame)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [name]);

  const handleRun = useCallback(async () => {
    setRunning(true);
    setError("");
    try {
      const result = await runGame(name, 10);
      setRunResult(result);
      await incrementPlay(name);
      setGame((g) => (g ? { ...g, play_count: g.play_count + 1 } : g));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Run failed");
    } finally {
      setRunning(false);
    }
  }, [name]);

  const handleRate = useCallback(
    async (rating: number) => {
      setUserRating(rating);
      try {
        const sessionId =
          sessionStorage.getItem("session_id") || crypto.randomUUID();
        sessionStorage.setItem("session_id", sessionId);
        const updated = await rateGame(name, rating, sessionId);
        setGame(updated);
        setRatingSaved(true);
      } catch {
        setError("Failed to save rating");
      }
    },
    [name],
  );

  if (loading) {
    return <p className="text-gray-400">Loading...</p>;
  }

  if (!game) {
    return <p className="text-red-400">Game not found: {error || name}</p>;
  }

  const screenshots = runResult?.screenshots || [];
  const gifUrl = runResult?.gif_url || null;
  const wsUrl = getWsPlayUrl(name);

  return (
    <div className="space-y-6">
      <a href="/" className="text-sm text-indigo-400 hover:text-indigo-300">
        ← Back to Gallery
      </a>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          {/* Interactive Game Player */}
          <GamePlayer gameName={name} wsUrl={wsUrl} controls={game.controls} />

          {/* Preview generation (secondary) */}
          <details className="text-sm">
            <summary className="text-gray-500 cursor-pointer hover:text-gray-300">
              Generate static preview
            </summary>
            <div className="mt-2 space-y-2">
              <button
                onClick={handleRun}
                disabled={running}
                className="px-4 py-1.5 rounded bg-gray-700 text-gray-300 text-sm hover:bg-gray-600 disabled:opacity-50"
              >
                {running ? "Generating..." : "Generate Preview"}
              </button>
              {runResult && (
                <>
                  <ScreenshotViewer screenshots={screenshots} gifUrl={gifUrl} />
                  <p className="text-xs text-gray-600">
                    Exit code: {runResult.exit_code} | Duration:{" "}
                    {runResult.duration_ms}ms
                  </p>
                </>
              )}
            </div>
          </details>
        </div>

        <div className="space-y-4">
          <h1 className="text-2xl font-bold">{game.display_name}</h1>

          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 text-xs rounded bg-indigo-900 text-indigo-300 capitalize">
              {game.genre}
            </span>
            <span className="text-sm text-gray-400">
              by {game.author_name || "Anonymous"}
            </span>
          </div>

          <p className="text-gray-300 text-sm">{game.description}</p>

          <div className="space-y-1">
            <p className="text-sm text-gray-400">
              Screen: {game.screen_width}x{game.screen_height}
            </p>
            <p className="text-sm text-gray-400">Plays: {game.play_count}</p>
            <p className="text-sm text-gray-400">
              Rating: {game.avg_rating.toFixed(1)} / 5 ({game.rating_count}{" "}
              votes)
            </p>
          </div>

          {game.controls && (
            <div className="p-3 rounded bg-gray-800 border border-gray-700">
              <p className="text-xs text-gray-400 mb-1">Controls</p>
              <p className="text-sm text-white">{game.controls}</p>
            </div>
          )}

          <div className="p-3 rounded bg-gray-800 border border-gray-700 space-y-2">
            <p className="text-xs text-gray-400">Rate this game</p>
            <StarRatingInput value={userRating} onChange={handleRate} />
            {ratingSaved && (
              <p className="text-xs text-green-400">Rating saved!</p>
            )}
          </div>

          {game.preview_image_url && !runResult && (
            <div className="space-y-1">
              <p className="text-xs text-gray-400">Preview</p>
              <img
                src={screenshotUrl(game.preview_image_url)}
                alt="Preview"
                className="w-full rounded border border-gray-700"
              />
            </div>
          )}
        </div>
      </div>

      {error && <p className="text-red-400 text-sm">{error}</p>}
    </div>
  );
}
