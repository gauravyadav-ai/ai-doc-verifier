from fastapi import APIRouter, UploadFile, File, HTTPException
from app.pipeline.ocr import run_ocr, validate_file

# APIRouter is like a mini FastAPI app — we register it in main.py
router = APIRouter(prefix="/api/v1", tags=["verification"])


@router.post("/verify")
async def verify_document(file: UploadFile = File(...)):
    """
    Upload a document (image or PDF) and extract text via OCR.
    
    Accepts: JPEG, PNG, TIFF, BMP, PDF
    Max size: 10MB
    """
    # Read file bytes into memory
    file_bytes = await file.read()

    # Validate before doing any heavy processing
    validation = validate_file(
        filename=file.filename,
        content_type=file.content_type,
        file_size=len(file_bytes),
    )

    if not validation["is_valid"]:
        # 422 = Unprocessable Entity (bad input from client)
        raise HTTPException(status_code=422, detail=validation["error"])

    # Run OCR — this is where the actual work happens
    result = run_ocr(
        file_bytes=file_bytes,
        content_type=file.content_type,
        filename=file.filename,
    )

    return {
        "status": "success",
        "data": result,
    }


@router.get("/supported-formats")
async def supported_formats():
    """Returns list of supported file types."""
    return {
        "images": ["image/jpeg", "image/png", "image/tiff", "image/bmp"],
        "documents": ["application/pdf"],
        "max_size_mb": 10,
    }
