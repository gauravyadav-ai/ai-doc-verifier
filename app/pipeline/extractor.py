import re
from typing import Any


# ── Regex patterns ──────────────────────────────────────────────

# Dates: matches DD/MM/YYYY, MM-DD-YYYY, "January 26, 2023", "26 Jan 2023" etc.
DATE_PATTERNS = [
    r'\b(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})\b',
    r'\b(\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2})\b',
    r'\b(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{2,4})\b',
    r'\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{2,4})\b',
]

# Emails
EMAIL_PATTERN = r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b'

# Phone numbers: handles +91, 10-digit, (xxx) xxx-xxxx formats
PHONE_PATTERNS = [
    r'\b(\+?\d{1,3}[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4})\b',
    r'\b(\+?91[\s\-]?\d{10})\b',
    r'\b(\d{10})\b',
]

# URLs
URL_PATTERN = r'https?://[^\s<>"{}|\\^`\[\]]+'
SHORTURL_PATTERN = r'\b(?:bit\.ly|tinyurl\.com|goo\.gl)/\S+'

# Currency amounts: ₹1,000  $500.00  USD 1000
AMOUNT_PATTERNS = [
    r'(?:₹|Rs\.?|INR|USD|\$|€|£)\s*[\d,]+(?:\.\d{2})?',
    r'\b[\d,]+(?:\.\d{2})?\s*(?:rupees?|dollars?|euros?)\b',
]

# Pincode / ZIP
PINCODE_PATTERN = r'\b\d{6}\b'   # Indian 6-digit pincode
ZIPCODE_PATTERN = r'\b\d{5}(?:\-\d{4})?\b'  # US ZIP


# ── Helper ───────────────────────────────────────────────────────

def _unique(items: list) -> list:
    """Remove duplicates while preserving order."""
    seen = set()
    result = []
    for item in items:
        clean = item.strip()
        if clean and clean not in seen:
            seen.add(clean)
            result.append(clean)
    return result


def _find_all(pattern: str, text: str, flags=re.IGNORECASE) -> list:
    return re.findall(pattern, text, flags)


# ── Main extractor ───────────────────────────────────────────────

def extract_features(text: str) -> dict[str, Any]:
    """
    Extract structured features from raw OCR text.
    
    Takes a plain text string, returns a dict of all found entities
    plus document-level stats.
    """
    if not text or not text.strip():
        return _empty_result()

    features: dict[str, Any] = {}

    # ── Entities ──
    # Dates
    dates = []
    for pattern in DATE_PATTERNS:
        dates.extend(_find_all(pattern, text))
    features["dates"] = _unique(dates)

    # Emails
    features["emails"] = _unique(_find_all(EMAIL_PATTERN, text))

    # Phone numbers
    phones = []
    for pattern in PHONE_PATTERNS:
        phones.extend(_find_all(pattern, text))
    features["phone_numbers"] = _unique(phones)

    # URLs
    urls = _find_all(URL_PATTERN, text)
    urls += _find_all(SHORTURL_PATTERN, text)
    features["urls"] = _unique(urls)

    # Amounts
    amounts = []
    for pattern in AMOUNT_PATTERNS:
        amounts.extend(_find_all(pattern, text, re.IGNORECASE))
    features["amounts"] = _unique(amounts)

    # Pincodes
    pincodes = _find_all(PINCODE_PATTERN, text)
    features["pincodes"] = _unique(pincodes)

    # ── Document stats ──
    lines = [l for l in text.split('\n') if l.strip()]
    words = text.split()

    features["stats"] = {
        "line_count": len(lines),
        "word_count": len(words),
        "char_count": len(text),
        # text density = words per line (higher = denser document)
        "text_density": round(len(words) / max(len(lines), 1), 2),
        # unique word ratio = vocabulary richness
        "unique_word_ratio": round(len(set(w.lower() for w in words)) / max(len(words), 1), 2),
    }

    # ── Key sections ──
    # Look for common document section headers
    section_keywords = [
        "summary", "objective", "experience", "education", "skills",
        "introduction", "conclusion", "terms", "conditions", "address",
        "signature", "date", "description", "name", "subject",
    ]
    found_sections = []
    text_lower = text.lower()
    for keyword in section_keywords:
        # Match keyword at start of line or after newline
        if re.search(r'(?:^|\n)\s*' + keyword, text_lower):
            found_sections.append(keyword)
    features["detected_sections"] = found_sections

    # ── Entity summary ──
    # Quick count of how many entity types were found
    features["entity_summary"] = {
        "has_dates": len(features["dates"]) > 0,
        "has_emails": len(features["emails"]) > 0,
        "has_phone_numbers": len(features["phone_numbers"]) > 0,
        "has_urls": len(features["urls"]) > 0,
        "has_amounts": len(features["amounts"]) > 0,
        "total_entities_found": (
            len(features["dates"]) +
            len(features["emails"]) +
            len(features["phone_numbers"]) +
            len(features["urls"]) +
            len(features["amounts"])
        ),
    }

    return features


def _empty_result() -> dict:
    """Return a clean empty result when text is blank."""
    return {
        "dates": [],
        "emails": [],
        "phone_numbers": [],
        "urls": [],
        "amounts": [],
        "pincodes": [],
        "stats": {
            "line_count": 0,
            "word_count": 0,
            "char_count": 0,
            "text_density": 0.0,
            "unique_word_ratio": 0.0,
        },
        "detected_sections": [],
        "entity_summary": {
            "has_dates": False,
            "has_emails": False,
            "has_phone_numbers": False,
            "has_urls": False,
            "has_amounts": False,
            "total_entities_found": 0,
        },
    }
