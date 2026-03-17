import pytest
from app.pipeline.classifier import classify_document, train_classifier


@pytest.fixture(scope="module")
def classifier():
    """Train once for all tests in this module."""
    train_classifier()


def test_classify_invoice(classifier):
    text = "Invoice number 1234 total amount due 5000 payment terms net 30 days"
    features = {"entity_summary": {"has_amounts": True, "has_dates": True,
                "has_emails": False, "has_urls": False, "has_phone_numbers": False,
                "total_entities_found": 2},
                "stats": {"word_count": 12}}
    result = classify_document(text, features)
    assert result["predicted_class"] == "invoice"
    assert result["confidence"] > 0.3


def test_classify_resume(classifier):
    text = "Resume curriculum vitae work experience education skills python java"
    features = {"entity_summary": {"has_amounts": False, "has_dates": False,
                "has_emails": True, "has_urls": False, "has_phone_numbers": False,
                "total_entities_found": 1},
                "stats": {"word_count": 10}}
    result = classify_document(text, features)
    assert result["predicted_class"] == "resume"


def test_classify_internship(classifier):
    text = "internship opportunity apply stipend duration months program training"
    features = {"entity_summary": {"has_amounts": False, "has_dates": True,
                "has_emails": True, "has_urls": True, "has_phone_numbers": False,
                "total_entities_found": 3},
                "stats": {"word_count": 10}}
    result = classify_document(text, features)
    assert result["predicted_class"] == "internship_notice"


def test_empty_text_returns_unknown(classifier):
    result = classify_document("", {})
    assert result["predicted_class"] == "unknown"
    assert result["confidence"] == 0.0


def test_confidence_is_between_0_and_1(classifier):
    text = "some random document text here"
    features = {"entity_summary": {"has_amounts": False, "has_dates": False,
                "has_emails": False, "has_urls": False, "has_phone_numbers": False,
                "total_entities_found": 0},
                "stats": {"word_count": 5}}
    result = classify_document(text, features)
    assert 0.0 <= result["confidence"] <= 1.0
