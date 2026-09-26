from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_check_text_valid_claim():
    payload = {
        "text": "Reuters reports that the central bank maintained benchmark interest rates unchanged following its monetary policy meeting."
    }
    response = client.post("/api/check-text", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "verdict" in data
    assert "confidence" in data
    assert "summary" in data
    assert "signals" in data
    assert "why_this_verdict" in data
    assert isinstance(data["signals"], list)
    # Check that confidence is between 0 and 100
    assert 0 <= data["confidence"] <= 100


def test_check_text_sensational():
    payload = {
        "text": "URGENT WARNING! SHOCKING MIRACLE CURE THEY DON'T WANT YOU TO KNOW! DRINK LEMON JUICE TO CURE ALL ILLNESSES 100% GUARANTEED! FORWARD TO ALL!"
    }
    response = client.post("/api/check-text", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] in ["Likely Misleading", "Likely False", "Insufficient Evidence"]
    assert "confidence" in data


def test_check_text_too_short():
    payload = {"text": "Too short"}
    response = client.post("/api/check-text", json=payload)
    assert response.status_code == 422  # Validation error
