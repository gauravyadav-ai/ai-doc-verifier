from fastapi import APIRouter, UploadFile, File, HTTPException
from app.pipeline.ocr import run_ocr, validate_file
from app.pipeline.extractor import extract_features
from app.pipeline.classifier import classify_document
from app.validator.rules import run_rules
from app.validator.ml_validator import compute_anomaly_score

router = APIRouter(prefix="/api/v1", tags=["verification"])


def compute_verdict(
    rule_results: dict,
    anomaly: dict,
    classification: dict,
) -> dict:
    """
    Combine rule engine + anomaly score into a final verdict.

    Scoring:
      Start at 1.0, apply rule penalties, apply anomaly penalty.
      >= 0.75 → PASS
      0.45–0.74 → REVIEW
      < 0.45 → FAIL
    """
    base_score = 1.0

    # Apply rule impacts
    base_score += rule_results["total_score_impact"]

    # Apply anomaly penalty (max -0.4 penalty)
    anomaly_penalty = anomaly["anomaly_score"] * 0.4
    base_score -= anomaly_penalty

    # Clamp between 0 and 1
    final_score = round(max(0.0, min(1.0, base_score)), 4)

    # Determine verdict
    if rule_results["error_count"] >= 2:
        # Hard fail: multiple errors regardless of score
        verdict = "FAIL"
    elif final_score >= 0.75:
        verdict = "PASS"
    elif final_score >= 0.45:
        verdict = "REVIEW"
    else:
        verdict = "FAIL"

    return {
        "verdict": verdict,
        "score": final_score,
        "score_pct": f"{final_score * 100:.1f}%",
        "error_count": rule_results["error_count"],
        "warning_count": rule_results["warning_count"],
        "is_anomalous": anomaly["is_anomalous"],
        "summary": _verdict_summary(verdict, final_score, rule_results, anomaly),
    }


def _verdict_summary(verdict, score, rule_results, anomaly) -> str:
    if verdict == "PASS":
        return f"Document passed verification with score {score*100:.0f}%."
    elif verdict == "REVIEW":
        issues = rule_results["warning_count"] + rule_results["error_count"]
        return f"Document requires manual review. {issues} issue(s) found, score {score*100:.0f}%."
    else:
        return (
            f"Document failed verification. "
            f"{rule_results['error_count']} error(s), "
            f"{rule_results['warning_count']} warning(s), score {score*100:.0f}%."
        )


@router.post("/verify")
async def verify_document(file: UploadFile = File(...)):
    """
    Full document verification pipeline:
    Upload → OCR → Features → Classification → Validation → Verdict
    """
    file_bytes = await file.read()

    # Step 1: validate file
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

    # Step 3: feature extraction
    features = extract_features(ocr_result["full_text"])

    # Step 4: ML classification
    classification = classify_document(ocr_result["full_text"], features)

    # Step 5: rule-based validation
    doc_type = classification["predicted_class"]
    rule_results = run_rules(doc_type, features, classification)

    # Step 6: anomaly detection
    anomaly = compute_anomaly_score(classification, features)

    # Step 7: final verdict
    verdict = compute_verdict(rule_results, anomaly, classification)

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
            "validation": {
                "rules": rule_results,
                "anomaly": anomaly,
            },
            "verdict": verdict,
        },
    }


@router.get("/supported-formats")
async def supported_formats():
    return {
        "images": ["image/jpeg", "image/png", "image/tiff", "image/bmp"],
        "documents": ["application/pdf"],
        "max_size_mb": 10,
    }
