"use client";

import { useBackendStatus } from "../hooks/use-backend-status";
import { cn } from "@/lib/utils";

const STATUS_COPY: Record<
  ReturnType<typeof useBackendStatus>,
  { label: string; detail: string }
> = {
  checking: {
    label: "Checking local signal",
    detail: "Looking for the on-device advisor",
  },
  connected: {
    label: "Running fully local",
    detail: "ChromaDB + Qwen 2.5 3B, no internet required",
  },
  offline: {
    label: "Advisor unreachable",
    detail: "Start the backend, or check Ollama is running",
  },
};

export function SignalStrip() {
  const status = useBackendStatus();
  const copy = STATUS_COPY[status];

  return (
    <div
      role="status"
      className="flex items-center gap-2.5 border-b border-line bg-husk px-4 py-2 text-xs sm:px-6"
    >
      <span className="relative flex h-2 w-2 shrink-0">
        <span
          className={cn(
            "h-2 w-2 rounded-full",
            status === "connected" && "bg-leaf",
            status === "checking" && "bg-harvest animate-signal",
            status === "offline" && "bg-terracotta",
          )}
        />
      </span>
      <span className="font-medium text-ink">{copy.label}</span>
      <span className="hidden text-ink/50 sm:inline">·</span>
      <span className="hidden font-utility text-ink/50 sm:inline">
        {copy.detail}
      </span>
    </div>
  );
}
