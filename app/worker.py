from celery import Celery
import os

# Create Celery app connected to Redis
celery_app = Celery(
    "doc_verifier",
    broker=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://redis:6379/0"),
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    result_expires=3600,      # Results expire after 1 hour
    task_track_started=True,  # Track when task starts (not just queued)
)


@celery_app.task(bind=True, name="verify_document_task")
def verify_document_task(self, file_bytes_hex: str, filename: str, content_type: str):
    """
    Background task that runs the full verification pipeline.
    
    bind=True gives us access to self (the task instance)
    so we can update task state during processing.
    
    file_bytes are passed as hex string because Celery
    serializes to JSON which can't handle raw bytes.
    """
    from app.pipeline.ocr import run_ocr, validate_file
    from app.pipeline.extractor import extract_features
    from app.pipeline.classifier import classify_document
    from app.validator.rules import run_rules
    from app.validator.ml_validator import compute_anomaly_score

    # Update task state so client knows we started
    self.update_state(state="PROCESSING", meta={"step": "ocr"})

    # Decode hex back to bytes
    file_bytes = bytes.fromhex(file_bytes_hex)

    # Validate
    validation = validate_file(filename, content_type, len(file_bytes))
    if not validation["is_valid"]:
        return {"status": "error", "error": validation["error"]}

    # OCR
    self.update_state(state="PROCESSING", meta={"step": "ocr"})
    ocr_result = run_ocr(file_bytes, content_type, filename)

    # Features
    self.update_state(state="PROCESSING", meta={"step": "extraction"})
    features = extract_features(ocr_result["full_text"])

    # Classification
    self.update_state(state="PROCESSING", meta={"step": "classification"})
    classification = classify_document(ocr_result["full_text"], features)

    # Validation
    self.update_state(state="PROCESSING", meta={"step": "validation"})
    doc_type = classification["predicted_class"]
    rule_results = run_rules(doc_type, features, classification)
    anomaly = compute_anomaly_score(classification, features)

    # Verdict
    from app.api.routes import compute_verdict
    verdict = compute_verdict(rule_results, anomaly, classification)

    return {
        "status": "success",
        "filename": filename,
        "content_type": content_type,
        "ocr": {
            "full_text": ocr_result["full_text"],
            "page_count": ocr_result["page_count"],
        },
        "features": features,
        "classification": classification,
        "validation": {
            "rules": rule_results,
            "anomaly": anomaly,
        },
        "verdict": verdict,
    }
