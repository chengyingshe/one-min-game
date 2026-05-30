"use client";

import { NpcPosition } from "@/lib/types";
import {
  MAP_BOUNDS,
  LOCATION_BUILDINGS,
  LOCATION_COORDS,
} from "@/lib/constants";
import MapCharacter from "./MapCharacter";

type Props = {
  positions: NpcPosition[];
  onNpcClick: (npcId: number) => void;
};

// Road connections between locations
const ROADS: [string, string][] = [
  ["茶馆", "书院"],
  ["茶馆", "集市"],
  ["书院", "河边"],
  ["集市", "河边"],
];

export default function TownMap({ positions, onNpcClick }: Props) {
  return (
    <div
      className="relative w-full overflow-hidden rounded-lg border border-stone-300 bg-stone-100"
      style={{ aspectRatio: `${MAP_BOUNDS.width}/${MAP_BOUNDS.height}` }}
    >
      {/* SVG Background: roads + buildings */}
      <svg
        viewBox={`0 0 ${MAP_BOUNDS.width} ${MAP_BOUNDS.height}`}
        className="absolute inset-0 h-full w-full"
        preserveAspectRatio="xMidYMid meet"
      >
        {/* Background fill */}
        <rect
          width={MAP_BOUNDS.width}
          height={MAP_BOUNDS.height}
          fill="#f5f0e8"
        />

        {/* Decorative ground patterns */}
        <pattern
          id="ground"
          width="20"
          height="20"
          patternUnits="userSpaceOnUse"
        >
          <rect width="20" height="20" fill="#e8e0d0" />
          <circle cx="10" cy="10" r="1" fill="#d4c8b0" />
        </pattern>
        <rect
          width={MAP_BOUNDS.width}
          height={MAP_BOUNDS.height}
          fill="url(#ground)"
          opacity="0.3"
        />

        {/* River decoration */}
        <path
          d={`M ${MAP_BOUNDS.width * 0.75} 0 Q ${MAP_BOUNDS.width * 0.8} 125 ${MAP_BOUNDS.width * 0.7} 250 Q ${MAP_BOUNDS.width * 0.65} 375 ${MAP_BOUNDS.width * 0.75} ${MAP_BOUNDS.height}`}
          stroke="#7ec8e3"
          strokeWidth="12"
          fill="none"
          opacity="0.4"
        />

        {/* Roads */}
        {ROADS.map(([from, to], i) => {
          const a = LOCATION_COORDS[from];
          const b = LOCATION_COORDS[to];
          return (
            <line
              key={i}
              x1={a.x}
              y1={a.y}
              x2={b.x}
              y2={b.y}
              stroke="#c4b89a"
              strokeWidth="6"
              strokeDasharray="8 4"
              opacity="0.6"
            />
          );
        })}

        {/* Center crossroads */}
        <circle cx={400} cy={220} r={8} fill="#c4b89a" opacity="0.5" />

        {/* Buildings */}
        {Object.entries(LOCATION_BUILDINGS).map(([name, b]) => (
          <g key={name}>
            <rect
              x={b.x}
              y={b.y}
              width={b.w}
              height={b.h}
              rx={6}
              fill="#d4c4a0"
              stroke="#a08c6a"
              strokeWidth="2"
            />
            {/* Roof */}
            <polygon
              points={`${b.x - 5},${b.y} ${b.x + b.w / 2},${b.y - 20} ${b.x + b.w + 5},${b.y}`}
              fill="#8b6c4a"
              stroke="#6b4c2a"
              strokeWidth="1.5"
            />
            {/* Label */}
            <text
              x={b.x + b.w / 2}
              y={b.y + b.h / 2 + 5}
              textAnchor="middle"
              fontSize="14"
              fill="#3e2c1a"
              fontWeight="bold"
            >
              {b.emoji} {b.label}
            </text>
          </g>
        ))}

        {/* Trees decoration */}
        {[
          [50, 50],
          [100, 400],
          [350, 400],
          [500, 180],
          [700, 50],
          [750, 400],
          [400, 450],
        ].map(([cx, cy], i) => (
          <g key={`tree-${i}`}>
            <circle cx={cx} cy={cy} r={10} fill="#6b8e4e" opacity="0.4" />
            <rect
              x={cx - 2}
              y={cy + 8}
              width={4}
              height={8}
              fill="#8b6c4a"
              opacity="0.4"
            />
          </g>
        ))}
      </svg>

      {/* NPC Characters */}
      {positions.map((npc) => (
        <MapCharacter
          key={npc.id}
          npc={npc}
          onClick={() => onNpcClick(npc.id)}
        />
      ))}
    </div>
  );
}
