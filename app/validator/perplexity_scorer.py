"""
Perplexity-based AI detection using a pretrained language model.

Perplexity measures how "surprised" a language model is by text.
- Low perplexity → model predicted the text easily → likely AI-generated
- High perplexity → model was surprised → likely human-written

This is the core signal used by GPTZero, Turnitin, and Originality.ai.

We use GPT-2 (small, 124M params) which runs on CPU in ~2-3 seconds.
"""

import math
import torch
from transformers import GPT2LMHeadModel, GPT2TokenizerFast
from typing import Optional

_model = None
_tokenizer = None
MODEL_NAME = "gpt2"


def _load_model():
    """Load GPT-2 once and cache it."""
    global _model, _tokenizer
    if _model is None:
        print("Loading GPT-2 model for perplexity scoring...")
        _tokenizer = GPT2TokenizerFast.from_pretrained(MODEL_NAME)
        _model = GPT2LMHeadModel.from_pretrained(MODEL_NAME)
        _model.eval()
        print("GPT-2 loaded.")
    return _model, _tokenizer


def compute_perplexity(text: str, max_length: int = 512) -> Optional[float]:
    """
    Compute perplexity of text using GPT-2.

    Lower perplexity = more AI-like
    Higher perplexity = more human-like

    Typical ranges:
      AI-generated text:  20 - 60  perplexity
      Human-written text: 60 - 200 perplexity

    Returns None if text is too short.
    """
    if not text or len(text.split()) < 20:
        return None

    try:
        model, tokenizer = _load_model()

        # Truncate to max_length tokens
        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=max_length,
        )

        input_ids = inputs["input_ids"]

        if input_ids.shape[1] < 10:
            return None

        with torch.no_grad():
            outputs = model(input_ids, labels=input_ids)
            loss = outputs.loss
            perplexity = math.exp(loss.item())

        return round(perplexity, 2)

    except Exception as e:
        print(f"Perplexity computation failed: {e}")
        return None


def interpret_perplexity(perplexity: Optional[float]) -> dict:
    """
    Convert perplexity score to AI probability contribution.

    Returns score contribution and interpretation.
    """
    if perplexity is None:
        return {
            "perplexity": None,
            "ai_score_contribution": 0.0,
            "interpretation": "insufficient_text",
        }

    # AI text: perplexity 20-55 → high AI probability
    # Mixed:   perplexity 55-80 → uncertain
    # Human:   perplexity 80+   → likely human
    if perplexity < 35:
        contribution = 0.45
        interpretation = "very_likely_ai"
    elif perplexity < 55:
        contribution = 0.30
        interpretation = "likely_ai"
    elif perplexity < 75:
        contribution = 0.15
        interpretation = "possibly_ai"
    elif perplexity < 100:
        contribution = 0.05
        interpretation = "borderline"
    else:
        contribution = 0.0
        interpretation = "likely_human"

    return {
        "perplexity": perplexity,
        "ai_score_contribution": contribution,
        "interpretation": interpretation,
    }
