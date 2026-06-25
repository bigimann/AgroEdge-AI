import { Sprout } from "lucide-react";

export function AppHeader() {
  return (
    <header className="border-b border-line bg-field px-4 py-4 sm:px-6">
      <div className="mx-auto flex max-w-3xl items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-leaf">
          <Sprout className="h-5 w-5 text-field" aria-hidden />
        </div>
        <div>
          <h1 className="font-display text-lg font-semibold leading-tight text-ink">
            AgroEdge AI
          </h1>
          <p className="text-xs leading-tight text-ink/50">
            Offline Agricultural Advisor
          </p>
        </div>
      </div>
    </header>
  );
}
