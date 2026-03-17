import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
import io
from typing import Union


# Supported file types
SUPPORTED_IMAGES = {"image/jpeg", "image/png", "image/tiff", "image/bmp"}
SUPPORTED_PDFS = {"application/pdf"}
MAX_FILE_SIZE_MB = 10


def validate_file(filename: str, content_type: str, file_size: int) -> dict:
    """
    Check file is valid before processing.
    Returns dict with is_valid bool and error message if invalid.
    """
    # Check file size (convert bytes to MB)
    size_mb = file_size / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        return {"is_valid": False, "error": f"File too large: {size_mb:.1f}MB. Max is {MAX_FILE_SIZE_MB}MB"}

    # Check file type
    all_supported = SUPPORTED_IMAGES | SUPPORTED_PDFS
    if content_type not in all_supported:
        return {"is_valid": False, "error": f"Unsupported file type: {content_type}"}

    return {"is_valid": True, "error": None}


def extract_text_from_image(image: Image.Image) -> str:
    """
    Run Tesseract OCR on a single PIL Image.
    Returns raw extracted text string.
    """
    # tesseract config:
    # --oem 3  = use LSTM neural net OCR engine (most accurate)
    # --psm 3  = fully automatic page segmentation (best for documents)
    config = "--oem 3 --psm 3"
    text = pytesseract.image_to_string(image, config=config)
    return text.strip()


def extract_text_from_pdf(file_bytes: bytes) -> list[str]:
    """
    Convert each PDF page to an image, then OCR each page.
    Returns list of strings, one per page.
    """
    # Convert PDF bytes → list of PIL Images (one per page)
    # dpi=200 is a good balance between speed and accuracy
    images = convert_from_bytes(file_bytes, dpi=200)

    pages_text = []
    for page_num, image in enumerate(images, start=1):
        text = extract_text_from_image(image)
        pages_text.append(text)

    return pages_text


def run_ocr(file_bytes: bytes, content_type: str, filename: str) -> dict:
    """
    Main OCR function. Accepts raw file bytes and returns structured result.
    This is what the API route will call.
    """
    result = {
        "filename": filename,
        "content_type": content_type,
        "page_count": 0,
        "pages": [],
        "full_text": "",
        "char_count": 0,
        "word_count": 0,
    }

    if content_type in SUPPORTED_IMAGES:
        # Single image → single page
        image = Image.open(io.BytesIO(file_bytes))
        text = extract_text_from_image(image)
        result["page_count"] = 1
        result["pages"] = [{"page": 1, "text": text}]
        result["full_text"] = text

    elif content_type in SUPPORTED_PDFS:
        # PDF → multiple pages
        pages_text = extract_text_from_pdf(file_bytes)
        result["page_count"] = len(pages_text)
        result["pages"] = [
            {"page": i + 1, "text": text}
            for i, text in enumerate(pages_text)
        ]
        result["full_text"] = "\n\n--- Page Break ---\n\n".join(pages_text)

    # Calculate stats on full extracted text
    result["char_count"] = len(result["full_text"])
    result["word_count"] = len(result["full_text"].split())

    return result
