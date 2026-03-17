import pytest
from app.validator.rules import run_rules
from app.validator.ml_validator import compute_anomaly_score


# ── Rule engine tests ────────────────────────────────────────────

def test_invoice_fails_without_amounts():
    features = {
        "entity_summary": {"has_amounts": False, "has_dates": True,
                           "has_emails": False, "has_urls": False,
                           "has_phone_numbers": False, "total_entities_found": 1},
        "stats": {"word_count": 50, "text_density": 3.0, "unique_word_ratio": 0.8},
        "detected_sections": [],
    }
    classification = {"confidence": 0.9}
    result = run_rules("invoice", features, classification)
    assert result["error_count"] >= 1


def test_invoice_passes_with_amounts_and_dates():
    features = {
        "entity_summary": {"has_amounts": True, "has_dates": True,
                           "has_emails": False, "has_urls": False,
                           "has_phone_numbers": False, "total_entities_found": 2},
        "stats": {"word_count": 80, "text_density": 4.0, "unique_word_ratio": 0.7},
        "detected_sections": [],
    }
    classification = {"confidence": 0.9}
    result = run_rules("invoice", features, classification)
    assert result["error_count"] == 0


def test_low_confidence_adds_warning():
    features = {
        "entity_summary": {"has_amounts": False, "has_dates": False,
                           "has_emails": False, "has_urls": False,
                           "has_phone_numbers": False, "total_entities_found": 0},
        "stats": {"word_count": 50, "text_density": 2.0, "unique_word_ratio": 0.6},
        "detected_sections": [],
    }
    classification = {"confidence": 0.2}
    result = run_rules("invoice", features, classification)
    assert result["error_count"] >= 1


def test_short_text_triggers_error():
    features = {
        "entity_summary": {"has_amounts": False, "has_dates": False,
                           "has_emails": False, "has_urls": False,
                           "has_phone_numbers": False, "total_entities_found": 0},
        "stats": {"word_count": 3, "text_density": 1.0, "unique_word_ratio": 1.0},
        "detected_sections": [],
    }
    classification = {"confidence": 0.8}
    result = run_rules("invoice", features, classification)
    assert result["error_count"] >= 1


# ── Anomaly detector tests ───────────────────────────────────────

def test_normal_doc_not_anomalous():
    classification = {
        "confidence": 0.9,
        "all_scores": {"invoice": 0.9, "resume": 0.05, "legal": 0.05},
    }
    features = {
        "stats": {"word_count": 100, "unique_word_ratio": 0.6},
        "entity_summary": {"total_entities_found": 3},
    }
    result = compute_anomaly_score(classification, features)
    assert result["is_anomalous"] is False


def test_ambiguous_scores_flagged():
    classification = {
        "confidence": 0.35,
        "all_scores": {"invoice": 0.35, "resume": 0.33, "legal": 0.32},
    }
    features = {
        "stats": {"word_count": 50, "unique_word_ratio": 0.5},
        "entity_summary": {"total_entities_found": 1},
    }
    result = compute_anomaly_score(classification, features)
    assert result["anomaly_score"] > 0.0
