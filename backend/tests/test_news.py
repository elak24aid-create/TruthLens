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
    news_router_module._NEWS_CACHE.clear()

@patch("app.routers.news.fetch_ddgs")
@patch("feedparser.parse")
@patch("urllib.request.urlopen")
def test_get_news_valid(mock_urlopen, mock_parse, mock_ddgs):
    mock_ddgs.return_value = []
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
    
@patch("app.routers.news.fetch_ddgs")
@patch("feedparser.parse")
@patch("urllib.request.urlopen")
def test_get_news_empty(mock_urlopen, mock_parse, mock_ddgs):
    mock_ddgs.return_value = []
    mock_parse.return_value = MockFeed([])
    response = client.get("/api/news")
    assert response.status_code == 200
    data = response.json()
    assert len(data["articles"]) == 0

@patch("app.routers.news.fetch_ddgs")
@patch("feedparser.parse")
@patch("urllib.request.urlopen")
def test_get_news_malformed(mock_urlopen, mock_parse, mock_ddgs):
    mock_ddgs.return_value = []
    # Entry missing title/link
    mock_parse.return_value = MockFeed([
        MockFeedEntry("", "http://test.com/2", "Summary")
    ])
    response = client.get("/api/news")
    assert response.status_code == 200
    data = response.json()
    # Should skip malformed
    assert len(data["articles"]) == 0

@patch("app.routers.news.fetch_ddgs")
@patch("feedparser.parse")
@patch("urllib.request.urlopen")
def test_get_news_duplicate(mock_urlopen, mock_parse, mock_ddgs):
    mock_ddgs.return_value = []
    mock_parse.return_value = MockFeed([
        MockFeedEntry("Same Title", "http://test.com/dup", "Summary 1"),
        MockFeedEntry("Same Title", "http://test.com/dup", "Summary 2"),
    ])
    response = client.get("/api/news")
    assert response.status_code == 200
    data = response.json()
    assert len(data["articles"]) == 1

@patch("app.routers.news.fetch_ddgs")
@patch("feedparser.parse")
@patch("urllib.request.urlopen")
def test_get_news_source_failure(mock_urlopen, mock_parse, mock_ddgs):
    mock_ddgs.return_value = []
    mock_parse.side_effect = Exception("Connection error")
    mock_urlopen.side_effect = Exception("Connection error")
    response = client.get("/api/news")
    assert response.status_code == 200
    data = response.json()
    assert len(data["articles"]) == 0

@patch("app.routers.news.fetch_ddgs")
@patch("feedparser.parse")
@patch("urllib.request.urlopen")
def test_get_news_pagination_limit(mock_urlopen, mock_parse, mock_ddgs):
    mock_ddgs.return_value = []
    entries = [MockFeedEntry(f"Title {i}", f"http://test.com/{i}", "Sum") for i in range(15)]
    mock_parse.return_value = MockFeed(entries)
    response = client.get("/api/news?limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["articles"]) == 2
