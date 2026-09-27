import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch
import app.routers.news as news_router_module

client = TestClient(app)

class MockFeedEntry:
    def __init__(self, title, link, summary, published_parsed=None, published=None):
        self.title = title
        self.link = link
        self.summary = summary
        if published_parsed:
            self.published_parsed = published_parsed
        if published:
            self.published = published
            
    def get(self, key, default=""):
        if key == "title": return getattr(self, "title", default)
        if key == "link": return getattr(self, "link", default)
        if key == "summary": return getattr(self, "summary", default)
        return default

class MockFeed:
    def __init__(self, entries):
        self.entries = entries

@pytest.fixture(autouse=True)
def clear_cache():
    # Clear the global cache before each test
    news_router_module._NEWS_CACHE["data"] = None
    news_router_module._NEWS_CACHE["timestamp"] = 0

@patch("feedparser.parse")
def test_get_news_valid(mock_parse):
    mock_parse.return_value = MockFeed([
        MockFeedEntry("Test Headline", "http://test.com/1", "Test summary")
    ])
    response = client.get("/api/news?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["articles"]) > 0
    assert data["articles"][0]["title"] == "Test Headline"
    assert data["articles"][0]["url"] == "http://test.com/1"
    
@patch("feedparser.parse")
def test_get_news_empty(mock_parse):
    mock_parse.return_value = MockFeed([])
    response = client.get("/api/news")
    assert response.status_code == 200
    data = response.json()
    assert len(data["articles"]) == 0

@patch("feedparser.parse")
def test_get_news_malformed(mock_parse):
    # Entry missing title/link
    mock_parse.return_value = MockFeed([
        MockFeedEntry("", "http://test.com/2", "Summary")
    ])
    response = client.get("/api/news")
    assert response.status_code == 200
    data = response.json()
    # Should skip malformed
    assert len(data["articles"]) == 0

@patch("feedparser.parse")
def test_get_news_duplicate(mock_parse):
    mock_parse.return_value = MockFeed([
        MockFeedEntry("Same Title", "http://test.com/dup", "Summary 1"),
        MockFeedEntry("Same Title", "http://test.com/dup", "Summary 2"), # duplicate URL and title
    ])
    response = client.get("/api/news")
    assert response.status_code == 200
    data = response.json()
    # Should only return one article because of deduplication
    assert len(data["articles"]) == 1

@patch("feedparser.parse")
def test_get_news_source_failure(mock_parse):
    mock_parse.side_effect = Exception("Connection error")
    # Because we loop over sources and catch exceptions per source, 
    # if all fail, it should just return an empty list (if cache is empty)
    response = client.get("/api/news")
    assert response.status_code == 200
    data = response.json()
    assert len(data["articles"]) == 0

@patch("feedparser.parse")
def test_get_news_pagination_limit(mock_parse):
    # Generate 15 entries
    entries = [MockFeedEntry(f"Title {i}", f"http://test.com/{i}", "Sum") for i in range(15)]
    mock_parse.return_value = MockFeed(entries)
    
    # But since we limit to 10 PER SOURCE in the router, if there's only 1 source returning these,
    # it will actually be capped at 10. Wait, the mock is called multiple times.
    # We will get up to 10 * num_sources. Let's just limit to 2 via query.
    response = client.get("/api/news?limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["articles"]) == 2
