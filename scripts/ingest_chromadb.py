import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Chroma client
client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="agriculture"
)

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

CHUNK_DIR = PROJECT_ROOT / "processed" / "chunks"

for file in CHUNK_DIR.glob("*.json"):

    print(f"Processing {file.name}")

    with open(file, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    # Added: Determine category flag before building individual chunk payloads
    if "soil" in file.name.lower():
        doc_category = "soil"
    else:
        doc_category = "crop"

    for i, chunk in enumerate(chunks):

        embedding = model.encode(chunk).tolist()

        collection.add(
            ids=[f"{file.stem}_{i}"],
            documents=[chunk],
            embeddings=[embedding],
            metadatas=[
                {
                    "source": file.stem,
                    "category": doc_category
                }
            ]
        )

print("Finished ingesting.")
