from fastapi import FastAPI
from app.api.routes import router
from app.pipeline.classifier import train_classifier

app = FastAPI(
    title="AI Document Verification System",
    description="OCR → Feature Extraction → ML Classification → Validation",
    version="0.3.0",
)

app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Train classifier on startup if not already trained."""
    print("Training document classifier...")
    train_classifier()
    print("Classifier ready.")


@app.get("/")
async def root():
    return {"status": "ok", "message": "AI Document Verifier is running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
