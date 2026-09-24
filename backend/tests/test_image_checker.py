import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw
import io

from backend.app.main import app
from backend.app.services import ocr_service

client = TestClient(app)

def test_check_image_success(monkeypatch):
    # Mock OCR extraction
    async def mock_extract(image_bytes):
        return "BREAKING NEWS: SHOCKING ALIEN DISCOVERY"
    
    monkeypatch.setattr("backend.app.routers.checker.extract_text_from_image", mock_extract)

    # Create a dummy image
    img = Image.new('RGB', (100, 100))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    image_bytes = buf.getvalue()

    response = client.post(
        "/api/check-image",
        files={"file": ("test.png", image_bytes, "image/png")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["ocr_text"] == "BREAKING NEWS: SHOCKING ALIEN DISCOVERY"
    assert data["claim_text"] == "BREAKING NEWS: SHOCKING ALIEN DISCOVERY"

def test_check_image_invalid_type():
    response = client.post(
        "/api/check-image",
        files={"file": ("test.txt", b"Hello", "text/plain")}
    )

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]

def test_check_image_too_large():
    # 11MB file
    large_bytes = b"0" * (11 * 1024 * 1024)
    response = client.post(
        "/api/check-image",
        files={"file": ("test.png", large_bytes, "image/png")}
    )

    assert response.status_code == 400
    assert "too large" in response.json()["detail"]

def test_check_image_no_text(monkeypatch):
    async def mock_extract(image_bytes):
        return "   " # Empty text
    
    monkeypatch.setattr("backend.app.routers.checker.extract_text_from_image", mock_extract)

    img = Image.new('RGB', (100, 100))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    image_bytes = buf.getvalue()

    response = client.post(
        "/api/check-image",
        files={"file": ("test.png", image_bytes, "image/png")}
    )

    assert response.status_code == 400
    assert "No readable news text" in response.json()["detail"]
