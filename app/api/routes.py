from fastapi import APIRouter, UploadFile, File, HTTPException
from app.pipeline.ocr import run_ocr, validate_file
from app.pipeline.extractor import extract_features
from app.pipeline.classifier import classify_document

router = APIRouter(prefix="/api/v1", tags=["verification"])


@router.post("/verify")
async def verify_document(file: UploadFile = File(...)):
    """
    Upload a document → OCR → feature extraction → ML classification.

    Accepts: JPEG, PNG, TIFF, BMP, PDF
    Max size: 10MB
    """
    file_bytes = await file.read()

    # Step 1: validate
    validation = validate_file(
        filename=file.filename,
        content_type=file.content_type,
        file_size=len(file_bytes),
    )
    if not validation["is_valid"]:
        raise HTTPException(status_code=422, detail=validation["error"])

    # Step 2: OCR
    ocr_result = run_ocr(
        file_bytes=file_bytes,
        content_type=file.content_type,
        filename=file.filename,
    )

    # Step 3: Feature extraction
    features = extract_features(ocr_result["full_text"])

    # Step 4: ML classification
    classification = classify_document(ocr_result["full_text"], features)

    return {
        "status": "success",
        "data": {
            "document": {
                "filename": ocr_result["filename"],
                "content_type": ocr_result["content_type"],
                "page_count": ocr_result["page_count"],
            },
            "ocr": {
                "full_text": ocr_result["full_text"],
                "pages": ocr_result["pages"],
            },
            "features": features,
            "classification": classification,
        },
    }


@router.get("/supported-formats")
async def supported_formats():
    return {
        "images": ["image/jpeg", "image/png", "image/tiff", "image/bmp"],
        "documents": ["application/pdf"],
        "max_size_mb": 10,
    }
