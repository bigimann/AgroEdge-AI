from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models import ChatRequest, ChatResponse
from app.services import rag_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the embedding model + Chroma collection once at startup instead
    # of on the first request. If ingestion hasn't been run yet (no
    # "agriculture" collection), fail loudly here rather than on first chat.
    try:
        rag_service.warm_up()
        print("AgroEdge AI backend ready: embedder + ChromaDB collection loaded.")
    except Exception as e:
        print(f"WARNING: startup warm-up failed ({e}). "
              f"Has ingest_chromadb.py been run yet?")
    yield


app = FastAPI(
    title="AgroEdge AI API",
    description="Offline-first AI agronomist backend (RAG over ChromaDB + Qwen 2.5 3B via Ollama)",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS: allow the Next.js frontend (default dev port 3000) to call this API.
# Adjust origins via env var in production rather than hardcoding.

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Accepts a farmer's question, retrieves relevant chunks from ChromaDB,
    and generates an answer via Qwen 2.5 3B (Ollama), citing sources.
    """
    try:
        result = rag_service.answer_question(request.question)
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate answer: {e}",
        )