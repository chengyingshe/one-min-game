"use client";

import { NpcConversation } from "@/lib/types";
import { LOCATION_COORDS, MAP_BOUNDS } from "@/lib/constants";

type Props = {
  conversations: NpcConversation[];
};

export default function ConversationFeed({ conversations }: Props) {
  if (conversations.length === 0) return null;

  return (
    <div className="rounded-lg border border-stone-300 bg-white/80 p-3">
      <h3 className="mb-2 text-sm font-bold text-stone-600">💬 小镇对话</h3>
      <div className="max-h-48 space-y-2 overflow-y-auto">
        {conversations.map((conv, ci) => (
          <div key={ci} className="rounded-md bg-emerald-50 px-3 py-2 text-xs">
            <div className="mb-1 font-semibold text-emerald-700">
              {conv.npc_a} & {conv.npc_b} 在{conv.location}
            </div>
            {conv.lines.map((line, li) => (
              <div key={li} className="py-0.5">
                <span className="font-medium text-stone-700">
                  {line.speaker}：
                </span>
                <span className="text-stone-600">{line.content}</span>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

// Floating dialogue bubbles shown on the map
export function DialogueBubbleOverlay({
  conversations,
}: {
  conversations: NpcConversation[];
}) {
  if (conversations.length === 0) return null;

  // Show bubble for the most recent conversation
  const latest = conversations[0];
  const locCoord = LOCATION_COORDS[latest.location];
  if (!locCoord) return null;

  const leftPct = (locCoord.x / MAP_BOUNDS.width) * 100;
  const topPct = ((locCoord.y - 60) / MAP_BOUNDS.height) * 100;

  return (
    <div
      className="pointer-events-none absolute z-20"
      style={{
        left: `${leftPct}%`,
        top: `${topPct}%`,
        transform: "translate(-50%, -100%)",
      }}
    >
      <div className="animate-fade-in rounded-lg bg-white/95 px-3 py-2 text-xs shadow-lg">
        <div className="font-semibold text-emerald-700">
          {latest.npc_a} ↔ {latest.npc_b}
        </div>
        {latest.lines.slice(-2).map((line, i) => (
          <div key={i} className="text-stone-700">
            <span className="font-medium">{line.speaker}：</span>
            {line.content}
          </div>
        ))}
        {/* Bubble tail */}
        <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 text-white">
          ▼
        </div>
      </div>
    </div>
  );
}
