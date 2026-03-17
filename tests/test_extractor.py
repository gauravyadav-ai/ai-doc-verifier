import pytest
from app.pipeline.extractor import extract_features


def test_extract_email():
    text = "Contact us at hello@example.com for more info."
    result = extract_features(text)
    assert "hello@example.com" in result["emails"]


def test_extract_date():
    text = "The deadline is January 26, 2023."
    result = extract_features(text)
    assert len(result["dates"]) > 0


def test_extract_url():
    text = "Apply at https://bit.ly/3wqZ2SJ before the deadline."
    result = extract_features(text)
    assert len(result["urls"]) > 0


def test_extract_amount():
    text = "Total payment due: ₹5,000 by next week."
    result = extract_features(text)
    assert len(result["amounts"]) > 0


def test_extract_pincode():
    text = "Address: University of Delhi, Delhi - 110021"
    result = extract_features(text)
    assert "110021" in result["pincodes"]


def test_empty_text_returns_empty_result():
    result = extract_features("")
    assert result["emails"] == []
    assert result["dates"] == []
    assert result["stats"]["word_count"] == 0


def test_stats_word_count():
    text = "one two three four five"
    result = extract_features(text)
    assert result["stats"]["word_count"] == 5


def test_entity_summary_flags():
    text = "Email: test@test.com, Date: 01/01/2023"
    result = extract_features(text)
    assert result["entity_summary"]["has_emails"] is True
    assert result["entity_summary"]["has_dates"] is True
    assert result["entity_summary"]["total_entities_found"] >= 2
