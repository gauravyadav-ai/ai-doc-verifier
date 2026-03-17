from sqlalchemy import create_engine, Column, String, Float, Integer, Text, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://docverify:docverify@postgres:5432/docverify"
).replace("postgresql+asyncpg", "postgresql")

# SQLite needs special connect args for thread safety in tests
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class VerificationResult(Base):
    __tablename__ = "verification_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(100), unique=True, index=True, nullable=False)
    filename = Column(String(255))
    content_type = Column(String(100))
    status = Column(String(20), default="pending")

    verdict = Column(String(20))
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
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
