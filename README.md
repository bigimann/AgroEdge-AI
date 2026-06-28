# AgroEdge AI

An offline-first AI agronomist for African farmers. Answers agricultural
questions using Retrieval-Augmented Generation (RAG) over a curated
knowledge base — Nigerian extension manuals, FAO guides, crop disease
manuals, and soil management resources — with every answer citing which
documents it came from.

Built for low-resource hardware, fully local: no cloud LLM, no internet
required once set up.

```text
PDF Documents → Text Extraction → Cleaning → Chunking → Embeddings
    → ChromaDB → Semantic Search → Qwen 2.5 3B (Ollama) → Answer + Sources
```

---

## Project structure

```text
agroedge-ai/
├── knowledge_base/
│   └── raw_pdfs/              ← source PDFs go here
├── processed/
│   ├── extracted_text/        ← output of extract_pdfs.py
│   ├── cleaned_text/          ← output of clean_txt.py
│   └── chunks/                ← output of chunk_documents.py
├── chroma_db/                 ← vector store (output of ingest_chromadb.py)
├── scripts/                   ← data pipeline (extract → clean → chunk → ingest)
│   ├── extract_pdfs.py
│   ├── clean_txt.py
│   ├── chunk_documents.py
│   ├── ingest_chromadb.py
│   ├── test_query.py
│   └── agro_rag.py
├── backend/                   ← FastAPI service (Phase 1)
│   ├── app/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── README.md
├── frontend/                  ← Next.js chat UI (Phase 2)
│   ├── app/, components/, hooks/, lib/, types/
│   ├── Dockerfile
│   ├── package.json
│   └── README.md
├── docker-compose.yml         ← runs backend + frontend in containers
├── .env.example                ← reference for every env var used (see below)
├── start.sh / start.bat        ← convenience: run both services together
├── stop.sh / stop.bat
└── README.md                   ← you are here
```

Each of `backend/` and `frontend/` has its own README with
service-specific detail. This file is the entry point and covers the
parts that connect them.

---

## Two ways to run this

|          | Plain (venv + npm)            | Docker                               |
| -------- | ----------------------------- | ------------------------------------ |
| Best for | Active development, debugging | Demoing, judging, "just make it run" |
| Ollama   | Native, either way            | **Always native** — see below        |
| Setup    | One-time per machine          | One-time per machine (image build)   |

Ollama is **never** containerized in either path. It needs efficient
access to your machine's CPU/GPU, and this project's whole premise is
local, low-resource inference — putting a virtualization layer in front
of that works against the goal. Install Ollama natively regardless of
which path you choose below.

---

## Path A: Plain (venv + npm)

### 1. Install and run Ollama

```bash
ollama pull qwen2.5:3b
ollama list   # should show qwen2.5:3b
```

Leave Ollama running (`ollama serve`, or just open the desktop app —
it usually runs as a background service after install).

### 2. Run the data pipeline (if you haven't already)

```bash
cd scripts
python extract_pdfs.py
python clean_txt.py
python chunk_documents.py
python ingest_chromadb.py
```

This populates `chroma_db/`. Skip this if it's already populated.

### 3. Set up the backend

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # optional — defaults work for local dev
```

**One-time, with internet connected:** download the embedding model.
This is the other thing (besides Ollama) that needs internet exactly
once, ever, per machine:

```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

Skipping this is the most common cause of "it works online but breaks
offline" — without the model cached, the backend can't load it at all
when there's no network, and every chat request fails with `Cannot
send a request, as the client has been closed`. Once it's downloaded
here, the backend genuinely never needs the network again for it
(`HF_HUB_OFFLINE=1` is set automatically).

### 4. Set up the frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
```

### 5. Run both

**Option A — convenience script** (after steps 1–4 above):

```bash
# macOS/Linux
./start.sh

# Windows
start.bat
```

This checks Ollama is reachable, starts the backend, waits for its
health check, then starts the frontend. Stop both with `./stop.sh` /
`stop.bat`.

**Option B — manual, two terminals:**

```bash
# Terminal 1
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000

# Terminal 2
cd frontend && npm run dev
```

Visit **http://localhost:3000**.

---

## Path B: Docker

### 1. Install and run Ollama (native, same as Path A, step 1)

```bash
ollama pull qwen2.5:3b
ollama list
```

This must be running on your **host machine** before starting
containers — the backend container reaches it over the network, not
inside the container.

### 2. Run the data pipeline (if you haven't already)

Same as Path A, step 2 — this runs on your host with your local Python,
not in Docker. It only needs to happen once; `chroma_db/` is then
mounted into the backend container as a volume.

### 3. Build and run

```bash
docker compose up --build
```

Visit **http://localhost:3000**.

### How the containers reach Ollama

This is the one detail that trips people up with Dockerized LLM apps,
so it's worth spelling out: a process inside a container can't reach
`localhost:11434` and expect that to mean "the host machine" — inside
the container, `localhost` means the container itself.

`docker-compose.yml` solves this with `OLLAMA_HOST=http://host.docker.internal:11434`,
plus an `extra_hosts` entry that makes `host.docker.internal` resolve on
Linux too (it resolves automatically on Docker Desktop for Mac/Windows
without that entry, but the line is harmless either way).

### Rebuilding after changes

```bash
docker compose up --build        # rebuild both
docker compose up --build backend # rebuild just one
docker compose down               # stop and remove containers
```

---

## Environment variables

The root `.env.example` documents every variable used by either
service in one place. In practice:

- **Plain venv**: copy `backend/.env.example` → `backend/.env` and
  `frontend/.env.local.example` → `frontend/.env.local`. Defaults work
  out of the box for local dev — you only need to edit these if you're
  changing ports, model names, or CORS origins.
- **Docker**: variables are set directly in `docker-compose.yml`
  (`environment:` and `build.args:`), not read from `.env` files inside
  the containers. Edit `docker-compose.yml` directly if you need to
  change them in that path.

| Variable              | Used by  | Default                                       | Purpose                                                                                       |
| --------------------- | -------- | --------------------------------------------- | --------------------------------------------------------------------------------------------- |
| `CHROMA_DB_PATH`      | backend  | auto-resolved `../chroma_db`                  | Where the vector store lives                                                                  |
| `OLLAMA_HOST`         | backend  | `http://localhost:11434`                      | Where Ollama is reachable                                                                     |
| `LLM_MODEL_NAME`      | backend  | `qwen2.5:3b`                                  | Which Ollama model to call                                                                    |
| `CORS_ORIGINS`        | backend  | `http://localhost:3000,http://127.0.0.1:3000` | Which frontend origins may call the API                                                       |
| `HF_HUB_OFFLINE`      | backend  | `1` (offline-only)                            | Skip the Hugging Face network check; set to `0` temporarily to download a new embedding model |
| `NEXT_PUBLIC_API_URL` | frontend | `http://localhost:8000`                       | Where the browser sends chat requests                                                         |

---

## Verifying it's working

1. **Ollama**: `ollama list` shows `qwen2.5:3b`.
2. **Backend health**: `curl http://localhost:8000/api/health` → `{"status":"ok"}`.
3. **Backend chat**:
   ```bash
   curl -X POST http://localhost:8000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"question": "What fertilizer should I use for maize?"}'
   ```
   should return an `answer` and a non-empty `sources` array.
4. **Frontend**: open `http://localhost:3000` — the signal strip under
   the header should turn green ("Running fully local") within a couple
   seconds. Ask a question and confirm you get an answer with a sources
   strip underneath it.

If something's off, each service's own README has a troubleshooting
section with more detail.

### Windows: "FATAL: An unexpected Turbopack error occurred"

If `npm run dev` repeatedly crashes with this message — often right
after the page loads fine, sometimes recurring on a fixed interval tied
to background requests like the signal strip's health check — this is
a known, unresolved Turbopack-on-Windows stability issue in current
Next.js versions, not a bug in this project's code. `frontend/package.json`
already runs dev mode as `next dev --webpack` to avoid it, since
webpack's dev server doesn't have this issue. If you're still seeing
it: confirm `package.json`'s `dev` script includes `--webpack`, then
delete `frontend/.next/` once to clear any stale cache from before the
switch, and restart `npm run dev`.

---

## Constraints this project honors

- ChromaDB is the only vector store — never replaced.
- Ollama + Qwen 2.5 3B is the only LLM — no OpenAI, no cloud inference.
- Everything runs local-first; internet is never required after setup.

## Architecture supports (not yet implemented)

- Farm planning (location, farm size, crop, budget → planting/fertilizer
  plan, risk factors, harvest timeline)
- Pest diagnosis via image upload
- Hausa language support
- Fuller offline mode (response caching, service worker)

The backend's `rag_service.py` and the frontend's `lib/` + `hooks/`
layers are deliberately separated from the API/UI surface so these can
be added without reworking the chat endpoint or chat screen.
