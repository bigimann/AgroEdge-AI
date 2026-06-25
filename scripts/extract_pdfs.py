from pathlib import Path
import pdfplumber
import pytesseract
from pdf2image import convert_from_path

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\Users\Welcome Sir\Downloads\poppler\Library\bin" 


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

PDF_DIR = PROJECT_ROOT / "knowledge_base" / "raw_pdfs"
OUTPUT_DIR = PROJECT_ROOT / "processed" / "extracted_text"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Prevent duplicate counting of lowercase/uppercase variations
pdf_files = list(set(PDF_DIR.glob("*.pdf")) | set(PDF_DIR.glob("*.PDF")))

if not pdf_files:
    print(f"Warning: No PDF files found in: {PDF_DIR.resolve()}")
else:
    print(f"Found {len(pdf_files)} PDF slices to analyze.")

for pdf_file in pdf_files:
    print(f"\nAnalyzing slice: {pdf_file.name}")
    text = ""
    is_scanned = False

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text and page_text.strip():
                text += page_text + "\n"
            else:
                is_scanned = True  

    if not text.strip() or is_scanned:
        print(f"-> Processing OCR for scanned contents on {pdf_file.name}...")
        text = ""  
        try:
            images = convert_from_path(pdf_file, dpi=100, poppler_path=POPPLER_PATH)
            
            for i, image in enumerate(images):
                print(f"  -> Processing page {i+1}/{len(images)}...")
                image = image.convert('L')
                page_text = ""
                rotation_success = False

                # Strategy 1: Attempt standard Auto-Rotation Check
                try:
                    osd = pytesseract.image_to_osd(image, timeout=4)
                    rotation = 0
                    for line in osd.split('\n'):
                        if 'Rotate' in line:
                            rotation = int(line.split(': ')[1])
                            break
                    if rotation != 0:
                        image = image.rotate(360 - rotation, expand=True)
                    
                    page_text = pytesseract.image_to_string(image, timeout=15)
                    if len(page_text.strip()) > 20: 
                        rotation_success = True
                except Exception:
                    pass

                # Strategy 2: Explicit Bruteforce Fallback (Eliminated array syntax completely)
                if not rotation_success or len(page_text.strip()) < 10:
                    print(f"     [!] Auto-rotation failed for Page {i+1}. Trying forced layout sweeps...")
                    best_text = page_text
                    
                    # Manual sweep check 1: Try Upside Down (180 degrees)
                    try:
                        img_180 = image.rotate(180, expand=True)
                        txt_180 = pytesseract.image_to_string(img_180, timeout=10)
                        if len(txt_180.strip()) > len(best_text.strip()):
                            best_text = txt_180
                    except Exception:
                        pass

                    # Manual sweep check 2: Try Sideways Left (90 degrees)
                    try:
                        img_90 = image.rotate(90, expand=True)
                        txt_90 = pytesseract.image_to_string(img_90, timeout=10)
                        if len(txt_90.strip()) > len(best_text.strip()):
                            best_text = txt_90
                    except Exception:
                        pass

                    # Manual sweep check 3: Try Sideways Right (270 degrees)
                    try:
                        img_270 = image.rotate(270, expand=True)
                        txt_270 = pytesseract.image_to_string(img_270, timeout=10)
                        if len(txt_270.strip()) > len(best_text.strip()):
                            best_text = txt_270
                    except Exception:
                        pass

                    page_text = best_text

                text += f"--- Page {i+1} ---\n{page_text}\n"
                    
        except Exception as e:
            print(f"OCR Error processing {pdf_file.name}: {e}")
            continue

    output_file = OUTPUT_DIR / f"{pdf_file.stem}.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"-> Successfully saved text extraction to: {output_file.name}")

print("\nAll tasks finished.")
