/**
 * Mirrors the FastAPI backend's Pydantic models exactly
 * (backend/app/models.py: ChatRequest, ChatResponse).
 */

export interface ChatRequest {
  question: string;
}

export interface ChatResponse {
  answer: string;
  sources: string[];
}

export type MessageRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  sources?: string[];
  /** Set when an assistant message represents a failed request. */
  isError?: boolean;
  createdAt: number;
}
