"use client";

import { useState } from "react";

const CHARACTER_SVG_MAP: Record<string, string> = {
  林黛玉: "/assets/svg/characters/lin_daiyu.svg",
  孙悟空: "/assets/svg/characters/sun_wukong.svg",
  张飞: "/assets/svg/characters/zhang_fei.svg",
};

type Props = {
  characterName: string;
  size?: "sm" | "md" | "lg";
  className?: string;
  showFallback?: boolean;
  fallbackEmoji?: string;
};

const SIZE_MAP = {
  sm: "w-12 h-18",
  md: "w-20 h-30",
  lg: "w-40 h-60",
};

export default function CharacterPortrait({
  characterName,
  size = "md",
  className = "",
  showFallback = false,
  fallbackEmoji,
}: Props) {
  const [imgError, setImgError] = useState(false);
  const svgPath = CHARACTER_SVG_MAP[characterName];

  if (showFallback || imgError || !svgPath) {
    return (
      <span
        className={`inline-flex items-center justify-center text-5xl ${className}`}
      >
        {fallbackEmoji || "👤"}
      </span>
    );
  }

  return (
    <div className={`${SIZE_MAP[size]} relative ${className}`}>
      <img
        src={svgPath}
        alt={characterName}
        className="h-full w-full object-contain"
        onError={() => setImgError(true)}
        loading="lazy"
      />
    </div>
  );
}
