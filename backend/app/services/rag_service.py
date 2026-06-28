"""
RAG service layer for AgroEdge AI.

This wraps the exact retrieval + generation logic from the working
agro_rag.py script as reusable functions, so the underlying pipeline
(ChromaDB + sentence-transformers + Ollama/Qwen) is untouched.

- embedding model: all-MiniLM-L6-v2
- vector store: ChromaDB PersistentClient at ./chroma_db, collection "agriculture"
- LLM: Ollama, model qwen2.5:3b
- prompt template: identical to agro_rag.py
"""

import os
from pathlib import Path
from functools import lru_cache

from dotenv import load_dotenv
import chromadb

os.environ.setdefault("HF_HUB_OFFLINE", "1")

from sentence_transformers import SentenceTransformer
import ollama

# Load backend/.env if present (no-op in Docker, where env vars are passed
# in directly via docker-compose and there is no .env file to find).

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

# Paths

# backend/app/services/rag_service.py -> backend/app -> backend -> project root

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

# CHROMA_DB_PATH can be overridden via env var (e.g. when running inside
# Docker, where chroma_db is mounted at a fixed container path rather than
# resolved relative to this file). Falls back to the same relative-path
# resolution used in plain venv setups.

CHROMA_DB_PATH = os.environ.get("CHROMA_DB_PATH", str(PROJECT_ROOT / "chroma_db"))

# OLLAMA_HOST can be overridden via env var. Needed in Docker, where the
# backend container must reach Ollama running natively on the host machine
# (e.g. http://host.docker.internal:11434) rather than localhost. Plain
# venv setups don't need to set this — the ollama library defaults to
# http://localhost:11434 on its own.

OLLAMA_HOST = os.environ.get("OLLAMA_HOST")
if OLLAMA_HOST:
    _ollama_client = ollama.Client(host=OLLAMA_HOST)
else:
    _ollama_client = ollama

COLLECTION_NAME = "agriculture"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
LLM_MODEL_NAME = os.environ.get("LLM_MODEL_NAME", "qwen2.5:3b")
TOP_K = 3

PROMPT_TEMPLATE = """
You are AgroEdge AI, an agricultural advisor for African farmers.

Answer ONLY using the information provided in the context.

If the answer is not found in the context, say:

"I do not have enough information in my knowledge base to answer that question."

Context:
{context}

Question:
{question}

Answer:
"""



# Lazily-loaded singletons

# These are expensive to load (embedding model into memory, Chroma client
# connection). Loading them once at process start (not per-request) keeps
# /api/chat fast on low-resource hardware.

@lru_cache(maxsize=1)
def get_embedder() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


@lru_cache(maxsize=1)
def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    return client.get_collection(COLLECTION_NAME)


def warm_up():
    """
    Force-load the embedder and Chroma collection once, e.g. at FastAPI
    startup, so the first real request isn't the one paying the load cost.
    Raises if the collection doesn't exist yet (i.e. ingestion hasn't run).
    """
    get_embedder()
    get_collection()



# Core RAG logic (same steps as agro_rag.py, just callable)

def retrieve(question: str, n_results: int = TOP_K):
    """
    Embed the question and query ChromaDB for the top matching chunks.
    Returns the raw Chroma query result dict.
    """
    embedder = get_embedder()
    collection = get_collection()

    query_embedding = embedder.encode(question).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
    )
    return results


def extract_sources(results) -> list[str]:
    """
    Pull unique 'source' values out of Chroma metadata, same as
    agro_rag.py's unique_sources logic. Order-preserving dedupe.
    """
    metadatas = results["metadatas"][0] if results["metadatas"] else []

    seen = set()
    sources: list[str] = []
    for meta in metadatas:
        source = meta.get("source")
        if source and source not in seen:
            seen.add(source)
            sources.append(source)
    return sources


def build_context(results) -> str:
    documents = results["documents"][0] if results["documents"] else []
    return "\n".join(documents)


def generate_answer(question: str, context: str) -> str:
    """
    Send the same prompt template used in agro_rag.py to Ollama/Qwen.
    """
    prompt = PROMPT_TEMPLATE.format(context=context, question=question)

    response = _ollama_client.chat(
        model=LLM_MODEL_NAME,
        messages=[
            {"role": "user", "content": prompt}
        ],
    )
    return response["message"]["content"]


def answer_question(question: str) -> dict:
    """
    Full pipeline used by POST /api/chat:
      1. retrieve top chunks
      2. extract sources
      3. build context
      4. generate answer
    Returns a dict matching the API response shape.
    """
    results = retrieve(question)
    sources = extract_sources(results)
    context = build_context(results)
    answer = generate_answer(question, context)

    return {
        "answer": answer,
        "sources": sources,
    }