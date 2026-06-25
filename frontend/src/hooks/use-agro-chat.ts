"use client";

import { useCallback, useState } from "react";
import type { ChatMessage } from "../types/chat";
import { askAgroEdge, ChatApiError } from "../lib/api";

function makeId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

export function useAgroChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = useCallback(
    async (question: string) => {
      const trimmed = question.trim();
      if (!trimmed || isLoading) return;

      const userMessage: ChatMessage = {
        id: makeId(),
        role: "user",
        content: trimmed,
        createdAt: Date.now(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);

      try {
        const result = await askAgroEdge(trimmed);
        const assistantMessage: ChatMessage = {
          id: makeId(),
          role: "assistant",
          content: result.answer,
          sources: result.sources,
          createdAt: Date.now(),
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } catch (error) {
        const message =
          error instanceof ChatApiError
            ? error.message
            : "Something went wrong while reaching the knowledge base.";

        const errorMessage: ChatMessage = {
          id: makeId(),
          role: "assistant",
          content: message,
          isError: true,
          createdAt: Date.now(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    },
    [isLoading],
  );

  return { messages, isLoading, sendMessage };
}
