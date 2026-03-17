import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from app.pipeline.ocr import run_ocr, validate_file
from app.pipeline.extractor import extract_features
from app.pipeline.classifier import classify_document
from app.validator.rules import run_rules
from app.validator.ml_validator import compute_anomaly_score
from app.database import get_db, VerificationResult

router = APIRouter(prefix="/api/v1", tags=["verification"])


# ── Shared verdict logic ─────────────────────────────────────────

def compute_verdict(rule_results, anomaly, classification):
    base_score = 1.0
    base_score += rule_results["total_score_impact"]
    base_score -= anomaly["anomaly_score"] * 0.4
    final_score = round(max(0.0, min(1.0, base_score)), 4)

    if rule_results["error_count"] >= 2:
        verdict = "FAIL"
    elif final_score >= 0.75:
        verdict = "PASS"
    elif final_score >= 0.45:
        verdict = "REVIEW"
    else:
        verdict = "FAIL"

    if verdict == "PASS":
        summary = f"Document passed verification with score {final_score*100:.0f}%."
    elif verdict == "REVIEW":
        issues = rule_results["warning_count"] + rule_results["error_count"]
        summary = f"Document requires manual review. {issues} issue(s) found, score {final_score*100:.0f}%."
    else:
        summary = (
            f"Document failed verification. "
            f"{rule_results['error_count']} error(s), "
            f"{rule_results['warning_count']} warning(s), score {final_score*100:.0f}%."
        )

    return {
        "verdict": verdict,
        "score": final_score,
        "score_pct": f"{final_score * 100:.1f}%",
        "error_count": rule_results["error_count"],
        "warning_count": rule_results["warning_count"],
        "is_anomalous": anomaly["is_anomalous"],
        "summary": summary,
    }


# ── Sync endpoint (immediate response) ──────────────────────────

@router.post("/verify")
async def verify_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Synchronous verification — waits for result, saves to DB."""
    file_bytes = await file.read()

    validation = validate_file(file.filename, file.content_type, len(file_bytes))
    if not validation["is_valid"]:
        raise HTTPException(status_code=422, detail=validation["error"])

    ocr_result = run_ocr(file_bytes, file.content_type, file.filename)
    features = extract_features(ocr_result["full_text"])
    classification = classify_document(ocr_result["full_text"], features)
    doc_type = classification["predicted_class"]
    rule_results = run_rules(doc_type, features, classification)
    anomaly = compute_anomaly_score(classification, features)
    verdict = compute_verdict(rule_results, anomaly, classification)

    # Save to database
    job_id = str(uuid.uuid4())
    record = VerificationResult(
        job_id=job_id,
        filename=ocr_result["filename"],
        content_type=ocr_result["content_type"],
        status="done",
        verdict=verdict["verdict"],
        score=verdict["score"],
        predicted_class=classification["predicted_class"],
        confidence=classification["confidence"],
        full_text=ocr_result["full_text"],
        features=features,
        classification=classification,
        validation={"rules": rule_results, "anomaly": anomaly},
        verdict_detail=verdict,
        completed_at=datetime.now(timezone.utc),
    )
    db.add(record)
    db.commit()

    return {
        "status": "success",
        "job_id": job_id,
        "data": {
            "document": {
                "filename": ocr_result["filename"],
                "content_type": ocr_result["content_type"],
                "page_count": ocr_result["page_count"],
            },
            "ocr": {"full_text": ocr_result["full_text"]},
            "features": features,
            "classification": classification,
            "validation": {"rules": rule_results, "anomaly": anomaly},
            "verdict": verdict,
        },
    }


# ── Async endpoint (returns job_id immediately) ──────────────────

@router.post("/verify/async")
async def verify_document_async(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Async verification — returns job_id immediately.
    Processing happens in background Celery worker.
    Poll GET /result/{job_id} for the result.
    """
    from app.worker import verify_document_task

    file_bytes = await file.read()

    validation = validate_file(file.filename, file.content_type, len(file_bytes))
    if not validation["is_valid"]:
        raise HTTPException(status_code=422, detail=validation["error"])

    # Save pending record
    job_id = str(uuid.uuid4())
    record = VerificationResult(
        job_id=job_id,
        filename=file.filename,
        content_type=file.content_type,
        status="pending",
    )
    db.add(record)
    db.commit()

    # Queue task (bytes → hex for JSON serialization)
    verify_document_task.apply_async(
        args=[file_bytes.hex(), file.filename, file.content_type],
        task_id=job_id,
    )

    return {
        "status": "queued",
        "job_id": job_id,
        "message": f"Poll GET /api/v1/result/{job_id} for results.",
    }


# ── Result retrieval ─────────────────────────────────────────────

@router.get("/result/{job_id}")
async def get_result(job_id: str, db: Session = Depends(get_db)):
    """Retrieve verification result by job ID."""
    record = db.query(VerificationResult).filter(
        VerificationResult.job_id == job_id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found.")

    return {
        "job_id": record.job_id,
        "status": record.status,
        "filename": record.filename,
        "created_at": record.created_at,
        "completed_at": record.completed_at,
        "verdict": record.verdict_detail,
        "classification": record.classification,
        "features": record.features,
        "validation": record.validation,
    }


# ── Job listing ──────────────────────────────────────────────────

@router.get("/jobs")
async def list_jobs(limit: int = 20, db: Session = Depends(get_db)):
    """List recent verification jobs."""
    records = (
        db.query(VerificationResult)
        .order_by(VerificationResult.created_at.desc())
        .limit(limit)
        .all()
    )

    return {
        "total": len(records),
        "jobs": [
            {
                "job_id": r.job_id,
                "filename": r.filename,
                "status": r.status,
                "verdict": r.verdict,
                "score": r.score,
                "predicted_class": r.predicted_class,
                "created_at": r.created_at,
            }
            for r in records
        ],
    }


@router.get("/supported-formats")
async def supported_formats():
    return {
        "images": ["image/jpeg", "image/png", "image/tiff", "image/bmp"],
        "documents": ["application/pdf"],
        "max_size_mb": 10,
    }
