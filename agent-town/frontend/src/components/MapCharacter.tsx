"use client";

import { NpcPosition } from "@/lib/types";
import { MAP_BOUNDS } from "@/lib/constants";

type Props = {
  npc: NpcPosition;
  onClick: () => void;
};

export default function MapCharacter({ npc, onClick }: Props) {
  const leftPct = (npc.pos_x / MAP_BOUNDS.width) * 100;
  const topPct = (npc.pos_y / MAP_BOUNDS.height) * 100;

  return (
    <div
      className="absolute z-10 cursor-pointer"
      style={{
        left: `${leftPct}%`,
        top: `${topPct}%`,
        transform: "translate(-50%, -100%)",
        transition: "left 2s ease-in-out, top 2s ease-in-out",
      }}
      onClick={onClick}
    >
      {/* Avatar */}
      <div className="flex flex-col items-center">
        <span className="text-2xl drop-shadow-lg">
          {npc.avatar_emoji || "👤"}
        </span>
        <span className="mt-0.5 whitespace-nowrap rounded bg-black/50 px-1.5 text-[10px] text-white">
          {npc.name}
        </span>
        {/* Moving indicator */}
        {npc.is_moving && (
          <span className="absolute -right-1 -top-1 text-xs">👣</span>
        )}
      </div>
    </div>
  );
}
