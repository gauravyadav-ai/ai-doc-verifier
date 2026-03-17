from sqlalchemy import create_engine, Column, String, Float, Integer, Text, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://docverify:docverify@postgres:5432/docverify"
).replace("postgresql+asyncpg", "postgresql")  # Use sync driver

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class VerificationResult(Base):
    """Stores every document verification result."""
    __tablename__ = "verification_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(100), unique=True, index=True, nullable=False)
    filename = Column(String(255))
    content_type = Column(String(100))
    status = Column(String(20), default="pending")   # pending/processing/done/error

    # Results (stored as JSON)
    verdict = Column(String(20))          # PASS / REVIEW / FAIL
    score = Column(Float)
    predicted_class = Column(String(50))
    confidence = Column(Float)
    full_text = Column(Text)
    features = Column(JSON)
    classification = Column(JSON)
    validation = Column(JSON)
    verdict_detail = Column(JSON)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)


def init_db():
    """Create tables if they don't exist."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency: yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
