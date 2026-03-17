import re
import pickle
import os
from typing import Any
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import LabelEncoder


# ── Document class definitions ───────────────────────────────────
# Each class has seed keywords that strongly indicate that doc type.
# We use these to build a synthetic training set.

DOC_CLASSES = {
    "invoice": [
        "invoice number amount due total tax payment billing",
        "invoice date vendor client bill to ship to subtotal",
        "payment terms net days purchase order invoice total gst",
        "invoice receipt amount payable bank transfer due date",
        "invoice no item description quantity unit price total amount",
    ],
    "resume": [
        "resume curriculum vitae work experience education skills",
        "objective summary professional experience references",
        "bachelor master degree university college gpa cgpa",
        "skills python java javascript frameworks linkedin github",
        "employment history projects internship volunteer achievements",
    ],
    "id_card": [
        "name date of birth address nationality identification",
        "aadhaar card pan card passport driving licence id number",
        "blood group gender male female dob issued expires",
        "voter id employee id student id card number valid",
        "identity proof government issued photo id document",
    ],
    "legal": [
        "agreement contract terms conditions parties herein",
        "whereas party agrees obligations rights liabilities",
        "jurisdiction governing law dispute resolution arbitration",
        "indemnification warranty disclaimer intellectual property",
        "signed executed witness notary legal binding enforceable",
    ],
    "internship_notice": [
        "internship opportunity apply stipend duration months",
        "internship program training learning project mentor",
        "eligibility criteria apply online last date selection",
        "internship opening position department institute college",
        "internship notice vacancy application form deadline submit",
    ],
    "academic": [
        "examination result marks grade pass fail percentage",
        "university college admission semester course syllabus",
        "certificate degree diploma awarded convocation",
        "student roll number subject marks obtained maximum",
        "academic transcript record performance evaluation",
    ],
    "medical": [
        "patient name diagnosis prescription medicine dosage",
        "doctor hospital clinic treatment symptoms report",
        "blood test report laboratory pathology sample",
        "medical certificate fitness health checkup discharge",
        "prescription tablets capsules mg ml twice daily",
    ],
    "bank_statement": [
        "account number balance transaction debit credit",
        "bank statement opening closing balance date narration",
        "ifsc swift branch account holder savings current",
        "withdrawal deposit transfer cheque upi neft rtgs",
        "statement period available balance ledger passbook",
    ],
}

MODEL_PATH = "/tmp/doc_classifier.pkl"


# ── Training ─────────────────────────────────────────────────────

def _build_training_data() -> tuple[list[str], list[str]]:
    """
    Build synthetic training data from keyword seeds.
    Each seed sentence becomes a training sample for its class.
    We also augment with combined sentences for robustness.
    """
    texts = []
    labels = []

    for doc_class, sentences in DOC_CLASSES.items():
        for sentence in sentences:
            texts.append(sentence)
            labels.append(doc_class)
            # Augment: combine two sentences to simulate real doc text
            for other_sentence in sentences:
                if other_sentence != sentence:
                    texts.append(f"{sentence} {other_sentence}")
                    labels.append(doc_class)

    return texts, labels


def train_classifier() -> Pipeline:
    """
    Train a TF-IDF + SGD classifier pipeline.
    
    TF-IDF converts text to feature vectors based on word frequency.
    SGD (Stochastic Gradient Descent) is fast and works well for text.
    
    Returns trained sklearn Pipeline.
    """
    texts, labels = _build_training_data()

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),   # Use single words AND word pairs
            max_features=5000,    # Top 5000 most important features
            sublinear_tf=True,    # Apply log scaling to term freq
            min_df=1,             # Include terms appearing at least once
        )),
        ("clf", SGDClassifier(
            loss="modified_huber",  # Gives probability estimates
            max_iter=1000,
            random_state=42,
            n_jobs=-1,              # Use all CPU cores
        )),
    ])

    pipeline.fit(texts, labels)

    # Save to disk so we don't retrain on every request
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(pipeline, f)

    print(f"Classifier trained on {len(texts)} samples, {len(DOC_CLASSES)} classes")
    return pipeline


def load_classifier() -> Pipeline:
    """Load classifier from disk, train if not exists."""
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)
    return train_classifier()


# ── Inference ────────────────────────────────────────────────────

# Module-level classifier instance (loaded once, reused on every request)
_classifier: Pipeline | None = None


def get_classifier() -> Pipeline:
    global _classifier
    if _classifier is None:
        _classifier = load_classifier()
    return _classifier


def classify_document(text: str, features: dict) -> dict[str, Any]:
    """
    Classify a document given its OCR text and extracted features.
    
    Returns predicted class, confidence score, and all class probabilities.
    """
    if not text or not text.strip():
        return {
            "predicted_class": "unknown",
            "confidence": 0.0,
            "all_scores": {},
            "is_confident": False,
        }

    clf = get_classifier()

    # Enrich the text with feature signals
    # This helps the classifier use entity info alongside raw text
    enriched = _enrich_text(text, features)

    # Get class probabilities
    classes = clf.classes_
    proba = clf.predict_proba([enriched])[0]

    # Build scores dict
    scores = {cls: round(float(prob), 4) for cls, prob in zip(classes, proba)}

    # Top prediction
    best_idx = np.argmax(proba)
    predicted_class = classes[best_idx]
    confidence = float(proba[best_idx])

    return {
        "predicted_class": predicted_class,
        "confidence": round(confidence, 4),
        "confidence_pct": f"{confidence * 100:.1f}%",
        # Confident if top score is clearly above others
        "is_confident": confidence >= 0.5,
        "all_scores": scores,
    }


def _enrich_text(text: str, features: dict) -> str:
    """
    Append feature signals as pseudo-words to the text.
    
    Example: if we found emails, append 'HAS_EMAIL HAS_EMAIL'
    so TF-IDF treats it as a strong signal.
    """
    signals = [text]

    entity_summary = features.get("entity_summary", {})

    if entity_summary.get("has_emails"):
        signals.append("HAS_EMAIL HAS_CONTACT")
    if entity_summary.get("has_amounts"):
        signals.append("HAS_AMOUNT HAS_MONEY FINANCIAL_DOCUMENT")
    if entity_summary.get("has_dates"):
        signals.append("HAS_DATE DATED_DOCUMENT")
    if entity_summary.get("has_urls"):
        signals.append("HAS_URL HAS_LINK")
    if entity_summary.get("has_phone_numbers"):
        signals.append("HAS_PHONE HAS_CONTACT")

    stats = features.get("stats", {})
    word_count = stats.get("word_count", 0)

    # Document length signals
    if word_count > 500:
        signals.append("LONG_DOCUMENT")
    elif word_count < 50:
        signals.append("SHORT_DOCUMENT")

    return " ".join(signals)
