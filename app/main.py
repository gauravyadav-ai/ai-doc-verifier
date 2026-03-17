from fastapi import FastAPI

app = FastAPI(
    title="AI Document Verification System",
    description="OCR → Feature Extraction → ML Classification → Validation",
    version="0.1.0",
)

@app.get("/")
async def root():
    return {"status": "ok", "message": "AI Document Verifier is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
