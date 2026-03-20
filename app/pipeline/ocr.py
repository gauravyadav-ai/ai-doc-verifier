import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
import pdfplumber
import io
from typing import Union


SUPPORTED_IMAGES = {"image/jpeg", "image/png", "image/tiff", "image/bmp"}
SUPPORTED_PDFS = {"application/pdf"}
MAX_FILE_SIZE_MB = 10


def validate_file(filename: str, content_type: str, file_size: int) -> dict:
    size_mb = file_size / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        return {"is_valid": False, "error": f"File too large: {size_mb:.1f}MB. Max is {MAX_FILE_SIZE_MB}MB"}
    all_supported = SUPPORTED_IMAGES | SUPPORTED_PDFS
    if content_type not in all_supported:
        return {"is_valid": False, "error": f"Unsupported file type: {content_type}"}
    return {"is_valid": True, "error": None}


def extract_text_from_image(image: Image.Image) -> str:
    """Run Tesseract OCR on a PIL image."""
    config = "--oem 3 --psm 3"
    text = pytesseract.image_to_string(image, config=config)
    return text.strip()


def extract_text_from_pdf_native(file_bytes: bytes) -> list[str]:
    """
    Use pdfplumber to extract text directly from text-based PDFs.
    This is much more accurate than OCR for PDFs with selectable text.
    Returns list of strings, one per page.
    """
    pages_text = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            pages_text.append(text.strip())
    return pages_text


def is_text_based_pdf(file_bytes: bytes) -> bool:
    """
    Check if a PDF contains selectable text.
    If yes → use pdfplumber (fast, accurate).
    If no → fall back to Tesseract OCR (for scanned PDFs).
    """
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                # If any page has more than 20 words, it's text-based
                if len(text.split()) > 20:
                    return True
        return False
    except Exception:
        return False


def extract_text_from_pdf_ocr(file_bytes: bytes) -> list[str]:
    """
    Fall back: convert PDF pages to images and OCR each one.
    Used for scanned PDFs where pdfplumber finds no text.
    """
    images = convert_from_bytes(file_bytes, dpi=200)
    pages_text = []
    for image in images:
        text = extract_text_from_image(image)
        pages_text.append(text)
    return pages_text


def run_ocr(file_bytes: bytes, content_type: str, filename: str) -> dict:
    """
    Main extraction function.

    Smart routing:
      - Images → Tesseract OCR
      - Text-based PDFs → pdfplumber (fast, accurate, full text)
      - Scanned PDFs → Tesseract OCR fallback
    """
    result = {
        "filename": filename,
        "content_type": content_type,
        "page_count": 0,
        "pages": [],
        "full_text": "",
        "char_count": 0,
        "word_count": 0,
        "extraction_method": "unknown",
    }

    if content_type in SUPPORTED_IMAGES:
        image = Image.open(io.BytesIO(file_bytes))
        text = extract_text_from_image(image)
        result["page_count"] = 1
        result["pages"] = [{"page": 1, "text": text}]
        result["full_text"] = text
        result["extraction_method"] = "tesseract_ocr"

    elif content_type in SUPPORTED_PDFS:
        # Smart routing: try pdfplumber first
        if is_text_based_pdf(file_bytes):
            pages_text = extract_text_from_pdf_native(file_bytes)
            result["extraction_method"] = "pdfplumber"
        else:
            # Scanned PDF — use OCR
            pages_text = extract_text_from_pdf_ocr(file_bytes)
            result["extraction_method"] = "tesseract_ocr"

        result["page_count"] = len(pages_text)
        result["pages"] = [
            {"page": i + 1, "text": text}
            for i, text in enumerate(pages_text)
        ]
        result["full_text"] = "\n\n".join(pages_text)

    result["char_count"] = len(result["full_text"])
    result["word_count"] = len(result["full_text"].split())

    return result
