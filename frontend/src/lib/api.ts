import type { ChatRequest, ChatResponse } from "../types/chat";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ??
  "http://localhost:8000";

export class ChatApiError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ChatApiError";
  }
}

/**
 * Calls the FastAPI backend's POST /api/chat endpoint.
 * Mirrors backend/app/main.py exactly: same request/response shape.
 */
export async function askAgroEdge(question: string): Promise<ChatResponse> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question } satisfies ChatRequest),
    });
  } catch {
    // Network-level failure: backend unreachable, offline, CORS, etc.
    throw new ChatApiError(
      "Can't reach the AgroEdge backend. Make sure the FastAPI server and Ollama are running.",
    );
  }

  if (!response.ok) {
    let detail = `Request failed with status ${response.status}.`;
    try {
      const body = await response.json();
      if (typeof body?.detail === "string") {
        detail = body.detail;
      }
    } catch {
      // response wasn't JSON; keep the generic detail message
    }
    throw new ChatApiError(detail);
  }

  const data = (await response.json()) as ChatResponse;
  return data;
}

/**
 * Calls the FastAPI backend's GET /api/health endpoint.
 * Used to drive the connection-status indicator.
 */
export async function checkBackendHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`, {
      method: "GET",
      cache: "no-store",
    });
    return response.ok;
  } catch {
    return false;
  }
}
