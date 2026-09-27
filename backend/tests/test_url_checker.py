import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, MagicMock
from app.services.url_extractor import is_safe_url

client = TestClient(app)

def test_is_safe_url():
    # Valid
    assert is_safe_url("https://www.google.com") == True
    assert is_safe_url("http://example.com/article/123") == True

    # Invalid
    assert is_safe_url("ftp://server") == False
    assert is_safe_url("file:///etc/passwd") == False
    assert is_safe_url("javascript:alert(1)") == False
    
    # SSRF / Private IPs
    assert is_safe_url("http://localhost") == False
    assert is_safe_url("http://127.0.0.1") == False
    assert is_safe_url("http://192.168.1.1") == False
    assert is_safe_url("http://10.0.0.5") == False
    assert is_safe_url("http://169.254.169.254") == False

def test_check_url_empty():
    response = client.post("/api/check-url", json={"url": "   "})
    assert response.status_code == 422 # Pydantic validation

def test_check_url_invalid_protocol():
    response = client.post("/api/check-url", json={"url": "ftp://test.com"})
    assert response.status_code == 422

@patch("app.services.url_extractor.urllib.request.urlopen")
def test_check_url_valid(mock_urlopen):
    # Mock successful fetch
    mock_response = MagicMock()
    mock_response.headers.get_content_type.return_value = "text/html"
    
    html_content = b"""
    <html>
        <head>
            <title>Breaking News</title>
            <meta property="og:description" content="This is a test article.">
            <meta property="og:site_name" content="Test News">
        </head>
        <body>
            <p>The quick brown fox jumps over the lazy dog.</p>
        </body>
    </html>
    """
    mock_response.read.return_value = html_content
    mock_urlopen.return_value.__enter__.return_value = mock_response

    response = client.post("/api/check-url", json={"url": "https://example.com"})
    assert response.status_code == 200
    data = response.json()
    assert "verdict" in data
    assert "summary" in data

@patch("app.services.url_extractor.urllib.request.urlopen")
def test_check_url_non_html(mock_urlopen):
    mock_response = MagicMock()
    mock_response.headers.get_content_type.return_value = "application/pdf"
    mock_urlopen.return_value.__enter__.return_value = mock_response

    response = client.post("/api/check-url", json={"url": "https://example.com/doc.pdf"})
    assert response.status_code == 400
    assert "Unsupported content type" in response.json()["detail"]

def test_check_url_ssrf():
    # Because 'localhost' fails our validation, it should return 400
    response = client.post("/api/check-url", json={"url": "http://localhost:8080/admin"})
    assert response.status_code == 400
    assert "Invalid or disallowed URL" in response.json()["detail"]
