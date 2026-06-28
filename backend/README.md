# AgroEdge AI — Backend

FastAPI wrapper around the existing, working RAG pipeline
(ChromaDB + `all-MiniLM-L6-v2` + Qwen 2.5 3B via Ollama).

> For full setup (Ollama, pipeline, frontend, Docker), start at the
> [root README](../README.md). This file covers backend-only details.

This does **not** change any of the existing pipeline scripts in
`../scripts/` (`extract_pdfs.py`, `clean_txt.py`, `chunk_documents.py`,
`ingest_chromadb.py`). It only exposes `agro_rag.py`'s logic over HTTP.

## Folder layout (for reference)

This folder lives inside the project root, alongside the data pipeline:

```text
agroedge-ai/
├── knowledge_base/
├── processed/
├── chroma_db/
├── scripts/
└── backend/      <- this folder
    ├── app/
    │   ├── main.py
    │   ├── models.py
    │   └── services/
    │       └── rag_service.py
    ├── Dockerfile
    └── requirements.txt
```

`rag_service.py` resolves `chroma_db` relative to its own file location
(four levels up) by default, so it finds `../chroma_db` automatically as
long as this folder structure is preserved. Override with the
`CHROMA_DB_PATH` env var if you move things around or run in Docker.

## Environment variables

All optional — sensible defaults are baked in for plain local dev.
Copy `.env.example` to `.env` to override any of them:

| Variable         | Default                                           | When you'd change it                                               |
| ---------------- | ------------------------------------------------- | ------------------------------------------------------------------ |
| `CHROMA_DB_PATH` | `../chroma_db` (resolved automatically)           | Docker, or non-standard folder layout                              |
| `OLLAMA_HOST`    | `http://localhost:11434` (ollama library default) | Docker (`http://host.docker.internal:11434`), or remote Ollama     |
| `LLM_MODEL_NAME` | `qwen2.5:3b`                                      | Using a different pulled model                                     |
| `CORS_ORIGINS`   | `http://localhost:3000,http://127.0.0.1:3000`     | Frontend served from a different origin                            |
| `HF_HUB_OFFLINE` | `1` (offline-only)                                | Set to `0` temporarily to download a new/different embedding model |

## Setup (plain venv)

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

### One-time: download the embedding model (requires internet, once)

This project is offline-first _after setup_ — but the embedding model
(`all-MiniLM-L6-v2`) has to be downloaded from Hugging Face the first
time, same as `qwen2.5:3b` has to be pulled via Ollama the first time.
With your venv active and internet connected:

```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

This caches the model locally (typically under
`~/.cache/huggingface`, or `C:\Users\<you>\.cache\huggingface` on
Windows). You only need to do this once per machine. After this, the
backend runs with `HF_HUB_OFFLINE=1` (set automatically — see Environment
variables above) and never touches the network again for this model,
even if your machine has no internet at all.

If you skip this step and try to start the backend offline, you'll see
`getaddrinfo failed` in the logs and every chat request will fail with
`Cannot send a request, as the client has been closed` — that error is
the symptom of the model never having been cached, not a bug to debug
further.

## Running (plain venv)

Make sure Ollama is running first (`ollama serve`, or the desktop app),
then:

```bash
uvicorn app.main:app --reload --port 8000
```

You should see on startup:

```
AgroEdge AI backend ready: embedder + ChromaDB collection loaded.
```

A warm-up warning instead almost always means `ingest_chromadb.py`
hasn't been run yet, or `chroma_db/` isn't where the backend expects it.

## Running (Docker)

See the root README and `docker-compose.yml`. Quick version:

```bash
# from the project root
docker compose up --build backend
```

## API

### Health check

```bash
curl http://localhost:8000/api/health
```

### Chat

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What fertilizer should I use for maize?"}'
```

Response:

```json
{
  "answer": "...",
  "sources": ["maize_guide", "soil_fertility_management"]
}
```

Note: `sources` returns the raw `source` value stored in ChromaDB
metadata at ingestion time (the cleaned-text filename stem, e.g.
`cleaned_maize_guide`, since `ingest_chromadb.py` reads from
`processed/chunks/`, which is built from `processed/cleaned_text/`).

Interactive docs: `http://localhost:8000/docs`

## What was intentionally left untouched

- ChromaDB (`PersistentClient`, collection `agriculture`).
- Embedding model (`all-MiniLM-L6-v2`, manual encoding).
- Ollama + `qwen2.5:3b`.
- Prompt template — identical to `agro_rag.py`.
- Retrieval count (`n_results=3`) — same as `agro_rag.py`.
