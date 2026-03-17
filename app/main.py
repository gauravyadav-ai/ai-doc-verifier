from fastapi import FastAPI
from app.api.routes import router
from app.pipeline.classifier import train_classifier
from app.database import init_db

app = FastAPI(
    title="AI Document Verification System",
    description="OCR → Feature Extraction → ML Classification → Validation",
    version="0.4.0",
)

app.include_router(router)


@app.on_event("startup")
async def startup_event():
    print("Initializing database...")
    init_db()
    print("Training document classifier...")
    train_classifier()
    print("System ready.")


@app.get("/")
async def root():
    return {"status": "ok", "message": "AI Document Verifier is running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
