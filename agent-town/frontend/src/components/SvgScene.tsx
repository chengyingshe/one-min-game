"use client";

import { useState } from "react";

const SCENE_SVG_MAP: Record<string, string> = {
  teahouse: "/assets/svg/scenes/teahouse.svg",
  market: "/assets/svg/scenes/market.svg",
  academy: "/assets/svg/scenes/academy.svg",
  riverside: "/assets/svg/scenes/riverside.svg",
};

type Props = {
  sceneName: string;
  className?: string;
  children?: React.ReactNode;
  fallbackGradient?: string;
  fallbackEmoji?: string;
};

export default function SvgScene({
  sceneName,
  className = "",
  children,
  fallbackGradient,
  fallbackEmoji,
}: Props) {
  const [loaded, setLoaded] = useState(false);
  const [imgError, setImgError] = useState(false);
  const svgPath = SCENE_SVG_MAP[sceneName];

  if (imgError || !svgPath) {
    return (
      <div
        className={`relative min-h-[300px] rounded-xl bg-gradient-to-b ${fallbackGradient || "from-amber-100 via-orange-50 to-yellow-50"} overflow-hidden ${className}`}
      >
        {fallbackEmoji && (
          <div className="absolute inset-0 flex items-center justify-center opacity-20">
            <span className="text-[180px] select-none">{fallbackEmoji}</span>
          </div>
        )}
        <div className="relative z-10">{children}</div>
      </div>
    );
  }

  return (
    <div
      className={`relative min-h-[300px] rounded-xl overflow-hidden ${className}`}
    >
      {/* Loading skeleton */}
      {!loaded && (
        <div
          className={`absolute inset-0 bg-gradient-to-b ${fallbackGradient || "from-amber-100 via-orange-50 to-yellow-50"} animate-pulse`}
        />
      )}
      {/* Scene SVG */}
      <img
        src={svgPath}
        alt={sceneName}
        className={`absolute inset-0 h-full w-full object-cover transition-opacity duration-500 ${
          loaded ? "opacity-100" : "opacity-0"
        }`}
        onLoad={() => setLoaded(true)}
        onError={() => setImgError(true)}
      />
      {/* Content overlay */}
      <div className="relative z-10">{children}</div>
    </div>
  );
}
