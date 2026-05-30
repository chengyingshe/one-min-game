"use client";

import { useState, useEffect, useCallback } from "react";
import { screenshotUrl } from "@/lib/api";

interface Props {
  screenshots: string[];
  gifUrl?: string | null;
}

export default function ScreenshotViewer({ screenshots, gifUrl }: Props) {
  const [index, setIndex] = useState(0);
  const [playing, setPlaying] = useState(false);

  const next = useCallback(() => {
    setIndex((i) => (i + 1) % screenshots.length);
  }, [screenshots.length]);

  const prev = useCallback(() => {
    setIndex((i) => (i - 1 + screenshots.length) % screenshots.length);
  }, [screenshots.length]);

  useEffect(() => {
    if (!playing || screenshots.length < 2) return;
    const id = setInterval(next, 400);
    return () => clearInterval(id);
  }, [playing, next, screenshots.length]);

  if (screenshots.length === 0) {
    return (
      <div className="aspect-video bg-gray-800 rounded-lg flex items-center justify-center text-gray-500">
        No screenshots yet. Click &quot;Generate Preview&quot; to capture.
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <div className="relative aspect-video bg-black rounded-lg overflow-hidden">
        <img
          src={screenshotUrl(screenshots[index])}
          alt={`Frame ${index + 1}`}
          className="w-full h-full object-contain"
        />
        {screenshots.length > 1 && (
          <div className="absolute bottom-0 left-0 right-0 flex items-center justify-between p-2 bg-gradient-to-t from-black/80">
            <button
              onClick={prev}
              className="px-2 py-1 rounded bg-white/20 text-white text-sm hover:bg-white/30"
            >
              ← Prev
            </button>
            <span className="text-white text-sm">
              {index + 1} / {screenshots.length}
            </span>
            <button
              onClick={next}
              className="px-2 py-1 rounded bg-white/20 text-white text-sm hover:bg-white/30"
            >
              Next →
            </button>
          </div>
        )}
      </div>

      <div className="flex gap-2 items-center">
        {screenshots.length > 1 && (
          <button
            onClick={() => setPlaying(!playing)}
            className="px-3 py-1 text-sm rounded bg-indigo-600 text-white hover:bg-indigo-500"
          >
            {playing ? "Pause" : "Auto-play"}
          </button>
        )}
        {gifUrl && (
          <a
            href={screenshotUrl(gifUrl)}
            target="_blank"
            rel="noopener noreferrer"
            className="px-3 py-1 text-sm rounded bg-gray-700 text-white hover:bg-gray-600"
          >
            View GIF
          </a>
        )}
      </div>
    </div>
  );
}
