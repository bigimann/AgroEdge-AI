export function ThinkingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="flex items-center gap-2 rounded-2xl rounded-tl-sm border border-line bg-white/60 px-4 py-3.5">
        <span className="flex gap-1">
          <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-leaf [animation-delay:-0.3s]" />
          <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-leaf [animation-delay:-0.15s]" />
          <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-leaf" />
        </span>
        <span className="font-utility text-xs text-ink/50">
          consulting the field manual
        </span>
      </div>
    </div>
  );
}
