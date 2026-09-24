import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.routers.report import _reports_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_db():
    _reports_db.clear()
    yield

def test_submit_report():
    response = client.post("/api/reports", json={
        "category": "Incorrect verdict",
        "verdict": "Likely Genuine",
        "content_summary": "Test text snippet",
        "comment": "I think this is wrong",
        "input_type": "text"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["id"] is not None
    assert data["status"] == "Submitted"
    assert data["category"] == "Incorrect verdict"
    assert data["comment"] == "I think this is wrong"
    
def test_submit_report_invalid():
    # Missing required category
    response = client.post("/api/reports", json={
        "verdict": "Likely Genuine",
        "content_summary": "Test text snippet",
        "input_type": "text"
    })
    assert response.status_code == 422
    
def test_get_reports():
    client.post("/api/reports", json={
        "category": "Misleading result",
        "verdict": "Likely Misleading",
        "content_summary": "First snippet",
        "input_type": "text"
    })
    
    response = client.get("/api/reports")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["category"] == "Misleading result"
    
def test_comment_length_limit():
    long_comment = "a" * 1500
    response = client.post("/api/reports", json={
        "category": "Other",
        "verdict": "Unverified",
        "content_summary": "Snippet",
        "comment": long_comment,
        "input_type": "text"
    })
    assert response.status_code == 422
