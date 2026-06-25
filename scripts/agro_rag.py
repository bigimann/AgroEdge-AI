import chromadb
from sentence_transformers import SentenceTransformer
import ollama

# Embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Chroma
client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_collection("agriculture")

question = input("Ask AgroEdge: ")

query_embedding = embedder.encode(question).tolist()

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3
)

sources = results["metadatas"][0]

unique_sources = set()

for source in sources:
    unique_sources.add(source["source"])

print("\nSources:")
for source in unique_sources:
    print("-", source)

context = "\n".join(results["documents"][0])

prompt = f"""
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

response = ollama.chat(
    model="qwen2.5:3b",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

print("\n")
print(response["message"]["content"])