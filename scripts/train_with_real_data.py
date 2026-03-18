import os
import sys
import pickle
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.pipeline.ocr import run_ocr
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import numpy as np

DATA_DIR = Path("data/training")
MODEL_PATH = Path("/tmp/doc_classifier.pkl")
SUPPORTED = {".pdf", ".jpg", ".jpeg", ".png", ".tiff"}

CONTENT_TYPES = {
    ".pdf": "application/pdf",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".tiff": "image/tiff",
}

def load_documents():
    texts, labels = [], []
    stats = {}
    for class_dir in sorted(DATA_DIR.iterdir()):
        if not class_dir.is_dir():
            continue
        class_name = class_dir.name
        files = [f for f in class_dir.iterdir() if f.suffix.lower() in SUPPORTED]
        if not files:
            print(f"  WARNING: No files in {class_dir}")
            continue
        print(f"  {class_name}: {len(files)} files...")
        stats[class_name] = 0
        for filepath in files:
            try:
                file_bytes = filepath.read_bytes()
                content_type = CONTENT_TYPES.get(filepath.suffix.lower(), "application/pdf")
                result = run_ocr(file_bytes, content_type, filepath.name)
                text = result["full_text"].strip()
                if len(text.split()) < 5:
                    continue
                texts.append(text)
                labels.append(class_name)
                stats[class_name] += 1
            except Exception as e:
                print(f"    ERROR {filepath.name}: {e}")
    return texts, labels, stats

def main():
    print("=" * 50)
    print("Training on real data")
    print("=" * 50)

    if not DATA_DIR.exists():
        print(f"ERROR: {DATA_DIR} not found.")
        sys.exit(1)

    print("\nLoading documents...")
    texts, labels, stats = load_documents()

    print(f"\nDataset:")
    for cls, count in stats.items():
        print(f"  {cls:<25} {count} samples")
    print(f"\n  Total: {len(texts)} samples")

    if len(texts) < 10:
        print("Not enough data.")
        sys.exit(1)

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=10000,
            sublinear_tf=True,
            min_df=1,
        )),
        ("clf", SGDClassifier(
            loss="modified_huber",
            max_iter=1000,
            random_state=42,
            n_jobs=-1,
        )),
    ])

    print(f"\nTraining on {len(X_train)} samples...")
    pipeline.fit(X_train, y_train)

    print(f"Evaluating on {len(X_test)} samples...\n")
    y_pred = pipeline.predict(X_test)
    print(classification_report(y_test, y_pred))

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(pipeline, f)
    print(f"Model saved to {MODEL_PATH}")
    print("\nRestart API: docker compose restart api")

if __name__ == "__main__":
    main()
