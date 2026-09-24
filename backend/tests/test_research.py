import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from unittest.mock import patch, MagicMock
from backend.app.schemas.research import ResearchRequest

client = TestClient(app)

def test_research_empty_claim():
    response = client.post("/api/research", json={"claim": "   "})
    assert response.status_code == 400
    assert "Claim cannot be empty" in response.json()["detail"]

def test_research_short_claim():
    response = client.post("/api/research", json={"claim": "short"})
    assert response.status_code == 200
    data = response.json()
    assert data["claim"] == "short"
    assert data["research_status"] == "insufficient_evidence"
    assert len(data["sources"]) == 0

@patch("duckduckgo_search.DDGS")
def test_research_valid_claim(mock_ddgs):
    # Mock DDGS responses
    mock_instance = MagicMock()
    mock_ddgs.return_value.__enter__.return_value = mock_instance
    mock_instance.text.return_value = [
        {"title": "Mars", "href": "https://en.wikipedia.org/wiki/Mars", "body": "Mars is the fourth planet from the Sun."}
    ]

    response = client.post("/api/research", json={"claim": "NASA confirms Mars is a planet."})
    assert response.status_code == 200
    data = response.json()
    assert data["claim"] == "NASA confirms Mars is a planet."
    assert data["research_status"] == "success"
    assert len(data["sources"]) == 1
    
    source = data["sources"][0]
    assert source["title"] == "Mars"
    assert source["url"] == "https://en.wikipedia.org/wiki/Mars"
    assert source["source_name"] == "en.wikipedia.org"

@patch("duckduckgo_search.DDGS")
def test_research_no_results(mock_ddgs):
    mock_instance = MagicMock()
    mock_ddgs.return_value.__enter__.return_value = mock_instance
    mock_instance.text.return_value = []
    response = client.post("/api/research", json={"claim": "A totally made up claim that yields no results."})
    assert response.status_code == 200
    data = response.json()
    assert data["research_status"] == "success"
    assert data["summary"] == "Insufficient online evidence found."
    assert len(data["sources"]) == 0

@patch("duckduckgo_search.DDGS")
def test_research_api_failure(mock_ddgs):
    mock_instance = MagicMock()
    mock_ddgs.return_value.__enter__.return_value = mock_instance
    mock_instance.text.side_effect = Exception("API down")
    response = client.post("/api/research", json={"claim": "Valid claim but API fails."})
    assert response.status_code == 200
    data = response.json()
    assert data["research_status"] == "error"
    assert "An error occurred" in data["summary"]
    assert len(data["sources"]) == 0
