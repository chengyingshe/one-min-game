"use client";

type Props = { day: number; time: string };

export default function WorldClock({ day, time }: Props) {
  return (
    <div className="flex items-center gap-2 rounded-full bg-amber-100/80 px-3 py-1 text-sm">
      <span className="text-amber-700">☀️</span>
      <span className="font-display text-ink-black">第{day}天</span>
      <span className="text-stone-400">·</span>
      <span className="font-mono text-stone-600">{time}</span>
    </div>
  );
}
