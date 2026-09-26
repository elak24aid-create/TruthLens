import pytest
from fastapi.testclient import TestClient
import io
import os
import cv2
import numpy as np

from backend.app.main import app
from backend.app.services import video_service

client = TestClient(app)

def create_dummy_video() -> bytes:
    # Create a simple 30-frame video
    temp_path = "temp_dummy_vid.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_path, fourcc, 10.0, (100, 100))
    for i in range(30):
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        # Put some text on it
        cv2.putText(frame, 'TEST NEWS', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        out.write(frame)
    out.release()
    
    with open(temp_path, 'rb') as f:
        data = f.read()
    
    os.remove(temp_path)
    return data

def test_check_video_success(monkeypatch):
    # Mock OCR extraction so we don't actually call WinRT OCR in the test
    async def mock_extract(image_bytes):
        return "BREAKING NEWS: SHOCKING ALIEN DISCOVERY"
    
    monkeypatch.setattr("backend.app.services.video_service.extract_text_from_image", mock_extract)

    video_bytes = create_dummy_video()

    response = client.post(
        "/api/check-video",
        files={"file": ("test.mp4", video_bytes, "video/mp4")}
    )

    assert response.status_code == 200
    data = response.json()
    assert "verdict" in data
    assert "summary" in data

def test_check_video_invalid_type():
    response = client.post(
        "/api/check-video",
        files={"file": ("test.txt", b"Hello", "text/plain")}
    )

    assert response.status_code == 400
    assert "Unsupported video format" in response.json()["detail"]

def test_check_video_too_large():
    # 51MB file
    large_bytes = b"0" * (51 * 1024 * 1024)
    response = client.post(
        "/api/check-video",
        files={"file": ("test.mp4", large_bytes, "video/mp4")}
    )

    assert response.status_code == 400
    assert "Invalid file size" in response.json()["detail"]

def test_check_video_no_text(monkeypatch):
    async def mock_extract(image_bytes):
        return "   " # Empty text
    
    monkeypatch.setattr("backend.app.services.video_service.extract_text_from_image", mock_extract)

    video_bytes = create_dummy_video()

    response = client.post(
        "/api/check-video",
        files={"file": ("test.mp4", video_bytes, "video/mp4")}
    )

    assert response.status_code == 200
    assert response.json()["verdict"] in ["Insufficient Evidence", "Likely False", "Likely Genuine"]
