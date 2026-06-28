# AgroEdge AI — Frontend

Next.js 15+ (App Router) chat interface for AgroEdge AI, calling the
FastAPI backend's `POST /api/chat` endpoint.

> For full setup (Ollama, pipeline, backend, Docker), start at the
> [root README](../README.md). This file covers frontend-only details.

## Design

A "field manual" aesthetic rather than a generic chat app: a serif
display face (Source Serif 4) for the identity, Inter for legible body
text on low-end screens, and a monospace utility face for source
citations — styled as a citation strip, not chat-bubble tags. The
**signal strip** under the header is the one signature element: a live,
honest indicator of whether the on-device advisor (ChromaDB + Qwen via
Ollama) is actually reachable, since "runs fully offline" is the real
value proposition of this product, not just a slogan.

## Environment variables

| Variable | Default | Notes |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Where the browser sends chat requests. In Docker, this is baked in at **build** time (see Dockerfile comment), not read at container start. |

## Setup (plain npm)

```bash
cd frontend
npm install
cp .env.local.example .env.local
```

## Running (plain npm)

Make sure the backend is running first (see `../backend/README.md`),
then:

```bash
npm run dev
```

Visit `http://localhost:3000`. The signal strip at the top will show
"Advisor unreachable" until the backend is up.

## Running (Docker)

See the root README and `docker-compose.yml`. Quick version:

```bash
# from the project root
docker compose up --build frontend
```

## Folder structure

```text
frontend/
├── app/
│   ├── layout.tsx        # fonts, metadata, root HTML shell
│   ├── page.tsx          # main chat page
│   └── globals.css       # design tokens (palette, type, focus states)
├── components/
│   ├── app-header.tsx
│   ├── signal-strip.tsx  # live backend connection indicator
│   ├── empty-state.tsx   # example questions before first message
│   ├── message-list.tsx
│   ├── chat-bubble.tsx   # renders answer + source citation strip
│   ├── thinking-indicator.tsx
│   ├── chat-input.tsx
│   └── ui/
│       └── button.tsx    # shadcn/ui-style primitive
├── hooks/
│   ├── use-agro-chat.ts      # message state + sendMessage
│   └── use-backend-status.ts # polls /api/health every 15s
├── lib/
│   ├── api.ts             # askAgroEdge(), checkBackendHealth()
│   └── utils.ts            # cn() class-merge helper
├── types/
│   └── chat.ts             # ChatRequest/ChatResponse, mirrors backend Pydantic models
└── Dockerfile
```

## API contract

This frontend assumes the backend's exact response shape:

```json
{
  "answer": "...",
  "sources": ["maize_guide", "soil_fertility_management"]
}
```

If the backend changes shape, update `types/chat.ts` and `lib/api.ts`
together — they're the only two files that know about the wire format.

## What's next

- Farm planning form, pest image upload, Hausa language toggle, offline
  response caching — `lib/api.ts` and `hooks/` are isolated from the UI
  components specifically so these can be added without reworking the
  chat screen.
