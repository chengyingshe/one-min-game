import { MemoryEntry } from "@/lib/types";
import { EMOTION_MAP } from "@/lib/constants";

const TIER_LABELS: Record<string, string> = {
  short_term: "🕐 近期",
  medium_term: "📝 印象",
  long_term: "💎 重要",
};

export default function MemoryCard({ memory }: { memory: MemoryEntry }) {
  const emotion = EMOTION_MAP[memory.emotion] || null;

  return (
    <div className="chinese-card p-3 text-sm">
      <div className="mb-1 flex items-center justify-between">
        <span className="text-xs text-stone-400">
          {TIER_LABELS[memory.tier] || memory.tier}
        </span>
        {emotion && (
          <span className="text-xs">
            {emotion.emoji} {emotion.label}
          </span>
        )}
      </div>
      <p className="leading-relaxed text-ink-black">{memory.event}</p>
      <div className="mt-2 flex items-center justify-between text-xs text-stone-400">
        <span>重要性: {Math.round(memory.importance)}</span>
        {memory.similarity !== undefined && (
          <span>相关度: {memory.similarity.toFixed(1)}</span>
        )}
      </div>
    </div>
  );
}
