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

@patch("backend.app.routers.research._fetch_ddg_sources")
def test_research_valid_claim(mock_ddgs):
    # Mock DDGS responses
    mock_ddgs.return_value = [
        {"title": "Mars", "url": "https://en.wikipedia.org/wiki/Mars", "source_name": "en.wikipedia.org", "snippet": "Mars is the fourth planet from the Sun.", "relevance": None, "published_date": None, "direction": "supporting"}
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

@patch("backend.app.routers.research._fetch_ddg_sources")
def test_research_no_results(mock_ddgs):
    mock_ddgs.return_value = []
    response = client.post("/api/research", json={"claim": "A totally made up claim that yields no results."})
    assert response.status_code == 200
    data = response.json()
    assert data["research_status"] == "success"
    assert data["summary"] == "Insufficient online evidence found."
    assert len(data["sources"]) == 0

@patch("backend.app.routers.research._fetch_ddg_sources")
def test_research_api_failure(mock_ddgs):
    mock_ddgs.side_effect = Exception("API down")
    response = client.post("/api/research", json={"claim": "Valid claim but API fails."})
    assert response.status_code == 200
    data = response.json()
    assert data["research_status"] == "error"
    assert "An error occurred" in data["summary"]
    assert len(data["sources"]) == 0
