import { BookText, AlertTriangle } from "lucide-react";
import type { ChatMessage } from "./../types/chat.ts";
import { cn } from "@/lib/utils";

export function ChatBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="max-w-[85%] rounded-2xl rounded-tr-sm bg-leaf px-4 py-3 text-field sm:max-w-[70%]">
          <p className="text-[15px] leading-relaxed">{message.content}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start">
      <div
        className={cn(
          "max-w-[90%] rounded-2xl rounded-tl-sm border px-4 py-3.5 sm:max-w-[75%]",
          message.isError
            ? "border-terracotta/30 bg-terracotta/5"
            : "border-line bg-white/60",
        )}
      >
        <div className="flex items-start gap-2.5">
          {message.isError && (
            <AlertTriangle
              className="mt-0.5 h-4 w-4 shrink-0 text-terracotta"
              aria-hidden
            />
          )}
          <p
            className={cn(
              "text-[15px] leading-relaxed whitespace-pre-wrap",
              message.isError ? "text-terracotta" : "text-ink",
            )}
          >
            {message.content}
          </p>
        </div>

        {message.sources && message.sources.length > 0 && (
          <div className="mt-3 border-t border-line/70 pt-2.5">
            <div className="flex items-center gap-1.5 text-[11px] font-medium uppercase tracking-wide text-harvest">
              <BookText className="h-3.5 w-3.5" aria-hidden />
              Sourced from
            </div>
            <ul className="mt-1.5 flex flex-wrap gap-1.5">
              {message.sources.map((source) => (
                <li
                  key={source}
                  className="rounded border border-harvest/30 bg-harvest/10 px-2 py-0.5 font-utility text-[11px] text-ink/80"
                >
                  {source}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
