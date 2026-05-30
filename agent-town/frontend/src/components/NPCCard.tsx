"use client";

import { NPC } from "@/lib/types";
import { NPC_META, EMOTION_MAP } from "@/lib/constants";
import CharacterPortrait from "./CharacterPortrait";

type Props = {
  npc: NPC;
  affection?: number;
  onClick?: () => void;
  compact?: boolean;
};

export default function NPCCard({ npc, affection, onClick, compact }: Props) {
  const meta = NPC_META[npc.name] || { emoji: "👤", color: "gray" };
  const emotion = EMOTION_MAP[npc.current_emotion] || {
    label: "平静",
    emoji: "😐",
  };

  return (
    <button
      onClick={onClick}
      className={`chinese-card text-left transition-all hover:scale-[1.02] hover:shadow-lg ${
        compact ? "p-3" : "p-4"
      }`}
    >
      <div className="flex items-center gap-3">
        <CharacterPortrait
          characterName={npc.name}
          size={compact ? "sm" : "md"}
          fallbackEmoji={npc.avatar_emoji || meta.emoji}
        />
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span className="font-display text-base">{npc.name}</span>
            <EmotionBadge emotion={npc.current_emotion} />
          </div>
          <p className="text-xs text-stone-400">
            《{npc.source}》· {npc.occupation}
          </p>
          {!compact && (
            <p className="mt-1 text-xs text-stone-500 line-clamp-1">
              {npc.speaking_style}
            </p>
          )}
        </div>
      </div>
      {affection !== undefined && (
        <div className="mt-2">
          <RelationshipBar value={affection} />
        </div>
      )}
    </button>
  );
}

function EmotionBadge({ emotion }: { emotion: string }) {
  const info = EMOTION_MAP[emotion] || { label: "平静", emoji: "😐" };
  return (
    <span className="inline-flex items-center gap-0.5 rounded-full bg-amber-100 px-1.5 py-0.5 text-xs">
      {info.emoji} {info.label}
    </span>
  );
}

function RelationshipBar({ value }: { value: number }) {
  const color =
    value >= 80
      ? "bg-green-500"
      : value >= 60
        ? "bg-jade-green"
        : value >= 40
          ? "bg-amber-400"
          : "bg-red-400";
  return (
    <div className="flex items-center gap-1.5">
      <span className="text-xs text-stone-400">好感</span>
      <div className="h-1.5 flex-1 rounded-full bg-stone-200">
        <div
          className={`h-full rounded-full transition-all ${color}`}
          style={{ width: `${value}%` }}
        />
      </div>
      <span className="text-xs text-stone-500 w-7 text-right">
        {Math.round(value)}
      </span>
    </div>
  );
}
