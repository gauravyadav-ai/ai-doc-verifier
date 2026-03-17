import pytest
import os

# Point tests at SQLite so no Postgres needed
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["SECRET_KEY"] = "test-secret"

from app.database import init_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create tables in SQLite before tests run."""
    init_db()
    yield
    # Cleanup
    if os.path.exists("test.db"):
        os.remove("test.db")
