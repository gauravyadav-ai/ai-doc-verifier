import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_supported_formats():
    response = client.get("/api/v1/supported-formats")
    assert response.status_code == 200
    data = response.json()
    assert "images" in data
    assert "documents" in data
    assert data["max_size_mb"] == 10


def test_verify_rejects_wrong_file_type():
    """Upload a .txt file — should get 422 error."""
    files = {"file": ("test.txt", b"some text content", "text/plain")}
    with patch("app.api.routes.get_db"):
        response = client.post("/api/v1/verify", files=files)
    assert response.status_code == 422


def test_verify_rejects_empty_file():
    """Upload oversized file — should get 422."""
    big_content = b"x" * (11 * 1024 * 1024)  # 11MB
    files = {"file": ("big.jpg", big_content, "image/jpeg")}
    with patch("app.api.routes.get_db"):
        response = client.post("/api/v1/verify", files=files)
    assert response.status_code == 422


def test_result_404_for_unknown_job():
    """Unknown job ID should return 404."""
    with patch("app.api.routes.get_db") as mock_db:
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_db.return_value = iter([mock_session])
        response = client.get("/api/v1/result/nonexistent-job-id")
    assert response.status_code == 404
