"""
AI-generated text detector.

Uses statistical signals to estimate the probability that
a document was written by an AI rather than a human.

Signals used:
  1. Burstiness    — humans vary sentence length a lot, AI is uniform
  2. Repetition    — AI repeats phrases more than humans
  3. N-gram diversity — AI reuses word combinations more
  4. Punctuation uniformity — AI uses punctuation very consistently
  5. Avg sentence length — AI tends toward medium-length sentences
"""

import re
import math
from collections import Counter
from typing import Any


def _get_sentences(text: str) -> list[str]:
    """Split text into sentences."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if len(s.strip()) > 10]


def _get_words(text: str) -> list[str]:
    """Get lowercase words."""
    return re.findall(r'\b[a-z]{2,}\b', text.lower())


def compute_burstiness(sentences: list[str]) -> float:
    """
    Burstiness measures how much sentence lengths vary.

    Human writing is bursty — short sentences mixed with long ones.
    AI writing is uniform — similar length throughout.

    Formula: (std / mean) — higher = more human-like
    If burstiness < 0.4 → likely AI (too uniform)
    """
    if len(sentences) < 4:
        return 1.0  # Not enough data, assume human

    lengths = [len(s.split()) for s in sentences]
    mean = sum(lengths) / len(lengths)
    if mean == 0:
        return 1.0

    variance = sum((l - mean) ** 2 for l in lengths) / len(lengths)
    std = math.sqrt(variance)
    return round(std / mean, 4)


def compute_repetition_score(words: list[str]) -> float:
    """
    Repetition score measures how often the same words appear.

    AI text tends to repeat key vocabulary more than humans.
    Score = 1 - (unique words / total words)
    Higher score = more repetitive = more AI-like
    """
    if not words:
        return 0.0

    unique = len(set(words))
    total = len(words)
    repetition = 1 - (unique / total)
    return round(repetition, 4)


def compute_ngram_diversity(words: list[str], n: int = 3) -> float:
    """
    N-gram diversity measures variety of word combinations.

    Low diversity = AI is reusing the same phrase patterns.
    Score = unique n-grams / total n-grams
    Lower score = less diverse = more AI-like
    """
    if len(words) < n + 1:
        return 1.0

    ngrams = [tuple(words[i:i+n]) for i in range(len(words)-n+1)]
    unique = len(set(ngrams))
    total = len(ngrams)
    return round(unique / total, 4)


def compute_punctuation_uniformity(sentences: list[str]) -> float:
    """
    Humans vary their punctuation naturally.
    AI tends to end sentences very uniformly (mostly periods).

    Returns fraction of sentences ending with period (high = AI-like).
    """
    if not sentences:
        return 0.0

    period_endings = sum(1 for s in sentences if s.strip().endswith('.'))
    return round(period_endings / len(sentences), 4)


def compute_avg_sentence_length(sentences: list[str]) -> float:
    """
    AI tends to write medium-length sentences (15-25 words).
    Very short or very long = more human-like.
    """
    if not sentences:
        return 0.0
    lengths = [len(s.split()) for s in sentences]
    return round(sum(lengths) / len(lengths), 2)


def detect_ai(text: str) -> dict[str, Any]:
    """
    Main AI detection function.

    Returns:
      ai_probability: 0.0 (human) → 1.0 (AI)
      verdict: HUMAN / REVIEW / AI_GENERATED
      signals: all computed signals
      flags: list of triggered AI flags
    """
    if not text or len(text.split()) < 30:
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

    # Compute all signals
    burstiness = compute_burstiness(sentences)
    repetition = compute_repetition_score(words)
    ngram_div = compute_ngram_diversity(words)
    punct_uniformity = compute_punctuation_uniformity(sentences)
    avg_sent_len = compute_avg_sentence_length(sentences)

    signals = {
        "burstiness": burstiness,
        "repetition_score": repetition,
        "ngram_diversity": ngram_div,
        "punctuation_uniformity": punct_uniformity,
        "avg_sentence_length": avg_sent_len,
        "sentence_count": len(sentences),
        "word_count": len(words),
    }

    # Score each signal (0 = human, 1 = AI)
    flags = []
    ai_score = 0.0

    # Signal 1: Low burstiness = AI uniform writing
    # Human burstiness typically > 0.5, AI < 0.4
    if burstiness < 0.3:
        ai_score += 0.35
        flags.append(f"Very low burstiness ({burstiness:.2f}) — AI writes uniformly structured sentences")
    elif burstiness < 0.45:
        ai_score += 0.2
        flags.append(f"Low burstiness ({burstiness:.2f}) — sentence lengths suspiciously uniform")

    # Signal 2: High repetition = AI vocabulary reuse
    # Human repetition typically < 0.6, AI > 0.7
    if repetition > 0.72:
        ai_score += 0.25
        flags.append(f"High repetition score ({repetition:.2f}) — vocabulary reuse typical of AI")
    elif repetition > 0.65:
        ai_score += 0.1
        flags.append(f"Moderate repetition ({repetition:.2f}) — slightly elevated vocabulary reuse")

    # Signal 3: Low n-gram diversity = AI phrase patterns
    # Human diversity typically > 0.85, AI < 0.75
    if ngram_div < 0.7:
        ai_score += 0.25
        flags.append(f"Low n-gram diversity ({ngram_div:.2f}) — repetitive phrase patterns detected")
    elif ngram_div < 0.8:
        ai_score += 0.1
        flags.append(f"Moderate n-gram diversity ({ngram_div:.2f}) — some phrase repetition")

    # Signal 4: High punctuation uniformity = AI
    # AI almost always ends sentences with periods
    if punct_uniformity > 0.92:
        ai_score += 0.1
        flags.append(f"Very uniform punctuation ({punct_uniformity:.2f}) — typical of AI text")

    # Signal 5: Very consistent sentence length
    # AI tends to write 15-25 word sentences consistently
    if 14 <= avg_sent_len <= 26 and burstiness < 0.5:
        ai_score += 0.05
        flags.append(f"Avg sentence length {avg_sent_len:.0f} words with low variance — AI pattern")

    # Clamp score
    ai_probability = round(min(ai_score, 1.0), 4)

    # Verdict
    if ai_probability >= 0.6:
        verdict = "AI_GENERATED"
    elif ai_probability >= 0.3:
        verdict = "REVIEW"
    else:
        verdict = "HUMAN"

    return {
        "ai_probability": ai_probability,
        "ai_probability_pct": f"{ai_probability * 100:.0f}%",
        "verdict": verdict,
        "is_ai_generated": ai_probability >= 0.6,
        "signals": signals,
        "flags": flags if flags else ["No AI patterns detected"],
    }
