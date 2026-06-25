from pathlib import Path
import json

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

TEXT_DIR = PROJECT_ROOT / "processed" / "cleaned_text"
OUTPUT_DIR = PROJECT_ROOT / "processed" / "chunks"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CHUNK_SIZE = 800
OVERLAP = 100

for txt_file in TEXT_DIR.glob("*.txt"):

    with open(txt_file, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = []

    start = 0

    while start < len(text):

        end = start + CHUNK_SIZE

        chunks.append(text[start:end])

        start += CHUNK_SIZE - OVERLAP

    output_file = OUTPUT_DIR / f"{txt_file.stem}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False)

print("Chunking complete.")