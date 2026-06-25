import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

# Input and Output Folders
INPUT_DIR = PROJECT_ROOT / "processed" / "extracted_text"
CLEANED_DIR = PROJECT_ROOT / "processed" / "cleaned_text"
CLEANED_DIR.mkdir(parents=True, exist_ok=True)

def clean_ocr_text(raw_text):
    """Applies cleaning rules to scrub dirty OCR artifacts from text."""
    # 1. Remove the custom script page headers we added earlier
    text = re.sub(r"--- Page \d+ (.*?)\s*---", "", raw_text)
    
    # 2. Fix broken hyphenated words at the end of lines (e.g., "agri-\nculture" -> "agriculture")
    text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
    
    # 3. Replace multiple newlines or tabs with a clean single spacing break
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    
    # 4. Strip out useless random OCR symbols/garbage characters (keeps standard letters, numbers, and punctuation)
    text = re.sub(r"[^\x20-\x7E\n]", "", text)
    
    # 5. Collapse multiple horizontal spaces into a single normal space
    text = re.sub(r" +", " ", text)
    
    return text.strip()

# Find all extracted text files
txt_files = list(INPUT_DIR.glob("*.txt"))

if not txt_files:
    print(f"No text files found to clean in: {INPUT_DIR.resolve()}")
else:
    print(f"Found {len(txt_files)} text files to clean.")

for txt_file in txt_files:
    print(f"Cleaning text for: {txt_file.name}")
    
    with open(txt_file, "r", encoding="utf-8") as f:
        raw_content = f.read()
        
    cleaned_content = clean_ocr_text(raw_content)
    
    # Save to the brand new cleaned directory
    output_file = CLEANED_DIR / f"cleaned_{txt_file.name}"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(cleaned_content)
        
    print(f"-> Saved clean data to: {output_file.name}")

print("\nData cleaning completely finished!")
