from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="AI Document Verification System",
    description="OCR → Feature Extraction → ML Classification → Validation",
    version="0.2.0",
)

# Register our API routes
app.include_router(router)


@app.get("/")
async def root():
    return {"status": "ok", "message": "AI Document Verifier is running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
