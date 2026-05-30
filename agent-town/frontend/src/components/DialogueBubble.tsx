type Props = {
  speakerType: "player" | "npc";
  speakerName: string;
  content: string;
  emotion?: string;
};

export default function DialogueBubble({
  speakerType,
  speakerName,
  content,
  emotion,
}: Props) {
  const isPlayer = speakerType === "player";

  return (
    <div className={`flex gap-2 ${isPlayer ? "flex-row-reverse" : ""}`}>
      {/* Avatar */}
      <div className="flex-shrink-0 flex items-center justify-center w-8 h-8 rounded-full bg-amber-200 text-sm">
        {isPlayer ? "🧑" : "🌸"}
      </div>

      {/* Bubble */}
      <div className={`max-w-[75%] ${isPlayer ? "items-end" : "items-start"}`}>
        <div className="flex items-baseline gap-2 mb-0.5">
          {!isPlayer && (
            <span className="text-xs font-display text-stone-500">
              {speakerName}
            </span>
          )}
          {emotion && !isPlayer && (
            <span className="text-xs text-stone-400">{emotion}</span>
          )}
          {isPlayer && <span className="text-xs text-stone-500">你</span>}
        </div>
        <div
          className={`rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
            isPlayer
              ? "bg-chinese-red text-white rounded-tr-md"
              : "bg-white border border-amber-200 text-ink-black rounded-tl-md"
          }`}
        >
          {content}
        </div>
      </div>
    </div>
  );
}
