import { EMOTION_MAP } from "@/lib/constants";

export function EmotionBadge({ emotion }: { emotion: string }) {
  const info = EMOTION_MAP[emotion] || { label: "平静", emoji: "😐" };
  return (
    <span className="inline-flex items-center gap-0.5 rounded-full bg-amber-100 px-1.5 py-0.5 text-xs">
      {info.emoji} {info.label}
    </span>
  );
}
