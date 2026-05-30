export default function LoadingSpinner({
  text = "角色思考中...",
}: {
  text?: string;
}) {
  return (
    <div className="flex items-center gap-2 py-4">
      <div className="flex gap-1">
        <span className="inline-block w-2 h-2 bg-amber-400 rounded-full animate-bounce [animation-delay:0ms]" />
        <span className="inline-block w-2 h-2 bg-amber-400 rounded-full animate-bounce [animation-delay:150ms]" />
        <span className="inline-block w-2 h-2 bg-amber-400 rounded-full animate-bounce [animation-delay:300ms]" />
      </div>
      <span className="text-sm text-stone-400">{text}</span>
    </div>
  );
}
