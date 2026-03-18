from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.routes import router
from app.pipeline.classifier import train_classifier
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing database...")
    init_db()
    print("Training document classifier...")
    train_classifier()
    print("System ready.")
    yield


app = FastAPI(
    title="AI Document Verification System",
    description="OCR → Feature Extraction → ML Classification → Validation",
    version="0.6.0",
    lifespan=lifespan,
)

app.include_router(router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
async def root():
    return FileResponse("app/static/index.html")


@app.get("/health")
async def health():
    return {"status": "healthy"}
