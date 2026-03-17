# AI Document Verification System

An end-to-end document verification pipeline using OCR, feature extraction, ML classification, and hybrid rule-based validation.

## Architecture
- OCR → Tesseract / EasyOCR
- Feature Extraction → text, layout, metadata parsing
- ML Classification → document type detection
- Validation → rule-based + ML hybrid
- REST API → FastAPI with async Celery task queue

## Quick Start

    cp .env.example .env
    docker compose up --build

API → http://localhost:8000
Docs → http://localhost:8000/docs

## Project Structure

    app/
      api/        → HTTP routes
      pipeline/   → OCR, extraction, classification
      validator/  → Rule engine and ML validation
    tests/        → Pytest suite
