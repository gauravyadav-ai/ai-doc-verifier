from typing import Any


# Each rule returns a dict with:
#   passed: bool
#   severity: "error" | "warning" | "info"
#   message: str
#   score_impact: float  (negative = bad, positive = good)

def _rule(passed: bool, severity: str, message: str, score_impact: float) -> dict:
    return {
        "passed": passed,
        "severity": severity,
        "message": message,
        "score_impact": score_impact if passed else -abs(score_impact),
    }


# ── Universal rules (apply to ALL doc types) ─────────────────────

def check_text_length(features: dict) -> dict:
    word_count = features.get("stats", {}).get("word_count", 0)
    if word_count < 10:
        return _rule(False, "error", f"Too little text extracted ({word_count} words). Possible blank or image-only document.", -0.4)
    elif word_count < 30:
        return _rule(False, "warning", f"Very short document ({word_count} words). May be incomplete.", -0.15)
    return _rule(True, "info", f"Text length acceptable ({word_count} words).", 0.1)


def check_classifier_confidence(classification: dict) -> dict:
    confidence = classification.get("confidence", 0)
    if confidence < 0.3:
        return _rule(False, "error", f"Classifier confidence very low ({confidence*100:.0f}%). Document type unclear.", -0.35)
    elif confidence < 0.5:
        return _rule(False, "warning", f"Classifier confidence low ({confidence*100:.0f}%). Needs manual review.", -0.15)
    return _rule(True, "info", f"Classifier confident ({confidence*100:.0f}%).", 0.1)


def check_text_density(features: dict) -> dict:
    density = features.get("stats", {}).get("text_density", 0)
    if density < 1.0:
        return _rule(False, "warning", "Very sparse text layout. May indicate a poorly scanned document.", -0.1)
    return _rule(True, "info", "Text density normal.", 0.05)


# ── Document-type specific rules ─────────────────────────────────

RULES_BY_TYPE = {
    "invoice": [
        lambda f, c: _rule(
            f.get("entity_summary", {}).get("has_amounts"),
            "error", "Invoice must contain monetary amounts.", -0.4
        ),
        lambda f, c: _rule(
            f.get("entity_summary", {}).get("has_dates"),
            "warning", "Invoice should contain a date.", -0.2
        ),
        lambda f, c: _rule(
            f.get("stats", {}).get("word_count", 0) >= 20,
            "warning", "Invoice seems too short to be valid.", -0.2
        ),
    ],
    "resume": [
        lambda f, c: _rule(
            len(f.get("detected_sections", [])) >= 2,
            "error", "Resume should have at least 2 sections (experience, education, skills, etc.).", -0.3
        ),
        lambda f, c: _rule(
            f.get("stats", {}).get("word_count", 0) >= 100,
            "warning", f"Resume only has {f.get('stats',{}).get('word_count',0)} words. Seems too short.", -0.2
        ),
        lambda f, c: _rule(
            f.get("entity_summary", {}).get("has_emails"),
            "warning", "Resume should contain a contact email.", -0.15
        ),
    ],
    "id_card": [
        lambda f, c: _rule(
            f.get("stats", {}).get("word_count", 0) <= 200,
            "warning", "ID card has too much text. May not be a valid ID card.", -0.2
        ),
        lambda f, c: _rule(
            f.get("entity_summary", {}).get("has_dates"),
            "warning", "ID card should contain a date (DOB or expiry).", -0.2
        ),
    ],
    "legal": [
        lambda f, c: _rule(
            f.get("stats", {}).get("word_count", 0) >= 100,
            "warning", "Legal document seems too short.", -0.25
        ),
        lambda f, c: _rule(
            f.get("entity_summary", {}).get("has_dates"),
            "info", "Legal document should contain execution date.", -0.1
        ),
    ],
    "internship_notice": [
        lambda f, c: _rule(
            f.get("entity_summary", {}).get("has_dates"),
            "warning", "Internship notice should contain application deadline.", -0.2
        ),
        lambda f, c: _rule(
            f.get("entity_summary", {}).get("has_emails") or
            f.get("entity_summary", {}).get("has_urls"),
            "warning", "Internship notice should contain contact info or apply link.", -0.15
        ),
    ],
    "academic": [
        lambda f, c: _rule(
            f.get("entity_summary", {}).get("has_dates"),
            "warning", "Academic document should contain a date.", -0.15
        ),
    ],
    "medical": [
        lambda f, c: _rule(
            f.get("entity_summary", {}).get("has_dates"),
            "warning", "Medical document should contain a date.", -0.2
        ),
    ],
    "bank_statement": [
        lambda f, c: _rule(
            f.get("entity_summary", {}).get("has_amounts"),
            "error", "Bank statement must contain monetary amounts.", -0.4
        ),
        lambda f, c: _rule(
            f.get("entity_summary", {}).get("has_dates"),
            "error", "Bank statement must contain transaction dates.", -0.3
        ),
    ],
}


def run_rules(
    doc_type: str,
    features: dict,
    classification: dict,
) -> dict[str, Any]:
    """
    Run all applicable rules for a document type.
    Returns rule results, total score impact, and error/warning counts.
    """
    results = []

    # Universal rules always run
    results.append(check_text_length(features))
    results.append(check_classifier_confidence(classification))
    results.append(check_text_density(features))

    # Type-specific rules
    type_rules = RULES_BY_TYPE.get(doc_type, [])
    for rule_fn in type_rules:
        results.append(rule_fn(features, classification))

    # Aggregate
    errors = [r for r in results if not r["passed"] and r["severity"] == "error"]
    warnings = [r for r in results if not r["passed"] and r["severity"] == "warning"]
    total_score_impact = sum(r["score_impact"] for r in results)

    return {
        "results": results,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "total_score_impact": round(total_score_impact, 4),
    }
