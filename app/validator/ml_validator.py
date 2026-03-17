from typing import Any


def compute_anomaly_score(
    classification: dict,
    features: dict,
) -> dict[str, Any]:
    """
    ML-based anomaly detection.

    Looks at the distribution of classifier scores to detect
    documents that don't clearly fit any known type.

    Returns anomaly score (0=normal, 1=highly anomalous) and flags.
    """
    all_scores = classification.get("all_scores", {})
    confidence = classification.get("confidence", 0)
    flags = []
    anomaly_score = 0.0

    if not all_scores:
        return {
            "anomaly_score": 1.0,
            "is_anomalous": True,
            "flags": ["No classification scores available"],
        }

    scores = list(all_scores.values())
    top_score = max(scores)
    second_score = sorted(scores, reverse=True)[1] if len(scores) > 1 else 0

    # Flag 1: top two classes are very close → ambiguous document
    score_gap = top_score - second_score
    if score_gap < 0.1:
        anomaly_score += 0.3
        flags.append(
            f"Ambiguous document: top two classes differ by only {score_gap:.2f}. "
            f"Could be misclassified."
        )

    # Flag 2: low overall confidence
    if confidence < 0.4:
        anomaly_score += 0.3
        flags.append(f"Low classifier confidence ({confidence*100:.0f}%).")

    # Flag 3: very short text is suspicious
    word_count = features.get("stats", {}).get("word_count", 0)
    if word_count < 15:
        anomaly_score += 0.25
        flags.append(f"Very little text ({word_count} words). OCR may have failed.")

    # Flag 4: no entities found at all
    total_entities = features.get("entity_summary", {}).get("total_entities_found", 0)
    if total_entities == 0 and word_count > 30:
        anomaly_score += 0.15
        flags.append("No structured entities found despite reasonable text length.")

    # Flag 5: unique word ratio too low → repeated text / garbage OCR
    unique_ratio = features.get("stats", {}).get("unique_word_ratio", 1.0)
    if unique_ratio < 0.2:
        anomaly_score += 0.2
        flags.append(
            f"Low vocabulary diversity ({unique_ratio:.2f}). "
            "Possible OCR noise or repeated content."
        )

    anomaly_score = min(round(anomaly_score, 4), 1.0)

    return {
        "anomaly_score": anomaly_score,
        "anomaly_pct": f"{anomaly_score * 100:.0f}%",
        "is_anomalous": anomaly_score >= 0.4,
        "flags": flags,
    }
