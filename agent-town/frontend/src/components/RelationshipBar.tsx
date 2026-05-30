export default function RelationshipBar({
  value,
  showLabel = true,
}: {
  value: number;
  showLabel?: boolean;
}) {
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
      {showLabel && <span className="text-xs text-stone-400">好感</span>}
      <div className="h-2 flex-1 rounded-full bg-stone-200">
        <div
          className={`h-full rounded-full transition-all duration-300 ${color}`}
          style={{ width: `${value}%` }}
        />
      </div>
      {showLabel && (
        <span className="w-7 text-right text-xs text-stone-500">
          {Math.round(value)}
        </span>
      )}
    </div>
  );
}
