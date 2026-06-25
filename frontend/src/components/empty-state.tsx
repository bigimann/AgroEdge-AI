import { Sprout } from "lucide-react";

const EXAMPLE_QUESTIONS = [
  "What fertilizer should I use for maize?",
  "How do I manage soil fertility in tropical Nigeria?",
  "What's the recommended spacing for cassava?",
  "How do I identify groundnut leaf spot disease?",
];

export function EmptyState({
  onPick,
}: {
  onPick: (question: string) => void;
}) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center px-6 py-12 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-leaf/10">
        <Sprout className="h-6 w-6 text-leaf" aria-hidden />
      </div>
      <h2 className="mt-4 font-display text-xl font-semibold text-ink">
        Ask the field manual anything
      </h2>
      <p className="mt-2 max-w-sm text-sm leading-relaxed text-ink/60">
        Answers are grounded in FAO guides, Nigerian extension manuals, and
        crop production handbooks already loaded on this device.
      </p>

      <div className="mt-6 flex w-full max-w-md flex-col gap-2">
        {EXAMPLE_QUESTIONS.map((question) => (
          <button
            key={question}
            type="button"
            onClick={() => onPick(question)}
            className="rounded-lg border border-line bg-white/50 px-4 py-2.5 text-left text-sm text-ink/80 transition-colors hover:border-leaf/40 hover:bg-leaf/5"
          >
            {question}
          </button>
        ))}
      </div>
    </div>
  );
}
