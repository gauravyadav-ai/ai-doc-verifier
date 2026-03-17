from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.routes import router
from app.pipeline.classifier import train_classifier
from app.database import init_db

app = FastAPI(
    title="AI Document Verification System",
    description="OCR → Feature Extraction → ML Classification → Validation",
    version="0.5.0",
)

app.include_router(router)

# Serve static files (our frontend)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.on_event("startup")
async def startup_event():
    print("Initializing database...")
    init_db()
    print("Training document classifier...")
    train_classifier()
    print("System ready.")


@app.get("/")
async def root():
    # Serve the frontend HTML at the root URL
    return FileResponse("app/static/index.html")


@app.get("/health")
async def health():
    return {"status": "healthy"}
