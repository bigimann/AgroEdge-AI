"use client";

import { useRef, useState, type KeyboardEvent } from "react";
import { ArrowUp } from "lucide-react";
import { Button } from "@/components/ui/button";

export function ChatInput({
  onSend,
  disabled,
}: {
  onSend: (question: string) => void;
  disabled: boolean;
}) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  function handleSubmit() {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  function handleInput(e: React.ChangeEvent<HTMLTextAreaElement>) {
    setValue(e.target.value);
    const el = e.target;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }

  return (
    <div className="border-t border-line bg-field px-4 py-3 sm:px-6 sm:py-4">
      <div className="mx-auto flex max-w-3xl items-end gap-2 rounded-xl border border-line bg-white/70 p-2 focus-within:border-leaf/50">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          rows={1}
          placeholder="Ask about crops, soil, pests, or fertilizer…"
          aria-label="Ask AgroEdge AI a question"
          className="max-h-40 flex-1 resize-none bg-transparent px-2 py-2 text-[15px] text-ink placeholder:text-ink/40 focus:outline-none disabled:opacity-50"
        />
        <Button
          type="button"
          size="icon"
          disabled={disabled || !value.trim()}
          onClick={handleSubmit}
          aria-label="Send question"
        >
          <ArrowUp className="h-4.5 w-4.5" />
        </Button>
      </div>
      <p className="mx-auto mt-2 max-w-3xl px-1 text-[11px] text-ink/40">
        AgroEdge AI answers only from its loaded knowledge base. It will say
        so if a question falls outside it.
      </p>
    </div>
  );
}
