import re
import math
from collections import Counter
from typing import Any


def _get_sentences(text: str) -> list[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if len(s.strip()) > 10]


def _get_words(text: str) -> list[str]:
    return re.findall(r'\b[a-z]{2,}\b', text.lower())


def compute_burstiness(sentences: list[str]) -> float:
    if len(sentences) < 3:
        return 1.0
    lengths = [len(s.split()) for s in sentences]
    mean = sum(lengths) / len(lengths)
    if mean == 0:
        return 1.0
    variance = sum((l - mean) ** 2 for l in lengths) / len(lengths)
    std = math.sqrt(variance)
    return round(std / mean, 4)


def compute_repetition_score(words: list[str]) -> float:
    if not words:
        return 0.0
    return round(1 - (len(set(words)) / len(words)), 4)


def compute_ngram_diversity(words: list[str], n: int = 3) -> float:
    if len(words) < n + 1:
        return 1.0
    ngrams = [tuple(words[i:i+n]) for i in range(len(words)-n+1)]
    return round(len(set(ngrams)) / len(ngrams), 4)


def compute_punctuation_uniformity(sentences: list[str]) -> float:
    if not sentences:
        return 0.0
    period_endings = sum(1 for s in sentences if s.strip().endswith('.'))
    return round(period_endings / len(sentences), 4)


def compute_paragraph_uniformity(text: str) -> float:
    """
    AI papers have very uniform paragraph lengths.
    Measure std/mean of paragraph word counts.
    Low value = uniform = AI-like.
    """
    paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 20]
    if len(paragraphs) < 2:
        return 1.0
    lengths = [len(p.split()) for p in paragraphs]
    mean = sum(lengths) / len(lengths)
    if mean == 0:
        return 1.0
    variance = sum((l - mean) ** 2 for l in lengths) / len(lengths)
    std = math.sqrt(variance)
    return round(std / mean, 4)


def compute_generic_phrase_score(text: str) -> float:
    """
    AI text is full of generic academic phrases.
    Count how many appear per 100 words.
    """
    generic_phrases = [
        "state-of-the-art", "experimental results", "future work",
        "significantly", "demonstrate", "propose", "novel approach",
        "in this paper", "we present", "our method", "baseline",
        "outperforms", "robustness", "scalable", "hybrid approach",
        "machine learning", "deep learning", "neural network",
        "accuracy", "precision", "recall", "evaluation",
        "traditional", "automated", "integrated", "leveraging",
        "furthermore", "moreover", "in conclusion", "highlights the",
        "this study", "findings suggest", "has become", "critical",
    ]
    text_lower = text.lower()
    word_count = max(len(text.split()), 1)
    hits = sum(1 for phrase in generic_phrases if phrase in text_lower)
    return round(hits / (word_count / 100), 4)


def detect_ai(text: str) -> dict[str, Any]:
    if not text or len(text.split()) < 15:
        return {
            "ai_probability": 0.0,
            "ai_probability_pct": "0%",
            "verdict": "INSUFFICIENT_TEXT",
            "signals": {},
            "flags": ["Not enough text to analyze"],
            "is_ai_generated": False,
        }

    sentences = _get_sentences(text)
    words = _get_words(text)

    burstiness = compute_burstiness(sentences)
    repetition = compute_repetition_score(words)
    ngram_div = compute_ngram_diversity(words)
    punct_uniformity = compute_punctuation_uniformity(sentences)
    para_uniformity = compute_paragraph_uniformity(text)
    generic_score = compute_generic_phrase_score(text)
    avg_sent_len = round(sum(len(s.split()) for s in sentences) / max(len(sentences), 1), 2)

    signals = {
        "burstiness": burstiness,
        "repetition_score": repetition,
        "ngram_diversity": ngram_div,
        "punctuation_uniformity": punct_uniformity,
        "paragraph_uniformity": para_uniformity,
        "generic_phrase_score": generic_score,
        "avg_sentence_length": avg_sent_len,
        "sentence_count": len(sentences),
        "word_count": len(words),
    }

    flags = []
    ai_score = 0.0

    # Signal 1: Burstiness
    if burstiness < 0.35:
        ai_score += 0.30
        flags.append(f"Very low burstiness ({burstiness:.2f}) — sentences are suspiciously uniform in length")
    elif burstiness < 0.50:
        ai_score += 0.20
        flags.append(f"Low burstiness ({burstiness:.2f}) — sentence length variance typical of AI writing")

    # Signal 2: Repetition
    if repetition > 0.65:
        ai_score += 0.20
        flags.append(f"High repetition ({repetition:.2f}) — vocabulary reuse typical of AI")
    elif repetition > 0.55:
        ai_score += 0.10
        flags.append(f"Moderate repetition ({repetition:.2f}) — elevated vocabulary reuse")

    # Signal 3: N-gram diversity
    if ngram_div < 0.85:
        ai_score += 0.20
        flags.append(f"Low n-gram diversity ({ngram_div:.2f}) — repetitive phrase patterns")
    elif ngram_div < 0.93:
        ai_score += 0.08
        flags.append(f"Moderate n-gram diversity ({ngram_div:.2f}) — some phrase repetition")

    # Signal 4: Punctuation uniformity
    if punct_uniformity > 0.95:
        ai_score += 0.15
        flags.append(f"Very uniform punctuation ({punct_uniformity:.2f}) — highly typical of AI text")
    elif punct_uniformity > 0.88:
        ai_score += 0.08
        flags.append(f"Uniform punctuation ({punct_uniformity:.2f}) — typical of AI text")

    # Signal 5: Paragraph uniformity (NEW — catches short AI papers)
    if para_uniformity < 0.35:
        ai_score += 0.25
        flags.append(f"Very uniform paragraph lengths ({para_uniformity:.2f}) — AI structures paragraphs evenly")
    elif para_uniformity < 0.55:
        ai_score += 0.15
        flags.append(f"Uniform paragraph structure ({para_uniformity:.2f}) — consistent paragraph sizing")

    # Signal 6: Generic phrases (NEW — catches AI academic writing)
    if generic_score > 3.0:
        ai_score += 0.25
        flags.append(f"High generic phrase density ({generic_score:.1f}/100 words) — overuse of AI cliches")
    elif generic_score > 1.5:
        ai_score += 0.12
        flags.append(f"Moderate generic phrases ({generic_score:.1f}/100 words) — elevated use of common AI expressions")

    # Signal 7: Sentence length in AI sweet spot
    if 13 <= avg_sent_len <= 22 and burstiness < 0.55:
        ai_score += 0.08
        flags.append(f"Avg sentence length {avg_sent_len:.0f} words with low variance — AI sweet spot")

    ai_probability = round(min(ai_score, 1.0), 4)

    if ai_probability >= 0.50:
        verdict = "AI_GENERATED"
    elif ai_probability >= 0.25:
        verdict = "REVIEW"
    else:
        verdict = "HUMAN"

    return {
        "ai_probability": ai_probability,
        "ai_probability_pct": f"{ai_probability * 100:.0f}%",
        "verdict": verdict,
        "is_ai_generated": ai_probability >= 0.50,
        "signals": signals,
        "flags": flags if flags else ["No AI patterns detected"],
    }
