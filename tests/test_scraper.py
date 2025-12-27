import pytest
from unittest.mock import patch, MagicMock
from arbitrage_os.discovery.scraper import scrape_url
import requests

@pytest.fixture(autouse=True)
def no_http_requests(monkeypatch):
    """Fixture to ensure no actual HTTP requests are made during tests."""
    def raise_error(*args, **kwargs):
        raise RuntimeError("Network request attempted during tests!")
    monkeypatch.setattr(requests, "get", raise_error)
    monkeypatch.setattr(requests, "post", raise_error)
    monkeypatch.setattr(requests, "put", raise_error)
    monkeypatch.setattr(requests, "delete", raise_error)

# Mock response for successful scraping
MOCK_HTML_SUCCESS = """
<html>
    <body>
        <h1>Test Title</h1>
        <p>This is some test content.</p>
        <img src="/images/test.jpg">
        <img src="http://example.com/images/another.png">
        <script>var a = 1;</script>
        <style>body {color: red;}</style>
    </body>
</html>
"""

# Mock response for empty content
MOCK_HTML_EMPTY = """
<html>
    <body>
        <script>var a = 1;</script>
        <style>body {color: red;}</style>
    </body>
</html>
"""

@patch('arbitrage_os.discovery.scraper.requests.get')
def test_scrape_url_success(mock_requests_get):
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = MOCK_HTML_SUCCESS.encode('utf-8')
    mock_response.raise_for_status.return_value = None
    mock_requests_get.return_value = mock_response

    url = "http://example.com/test"

    # Act
    result = scrape_url(url)

    # Assert
    assert "text" in result
    assert "image_urls" in result
    assert "Test Title\nThis is some test content." in result["text"]
    assert "http://example.com/images/test.jpg" in result["image_urls"]
    assert "http://example.com/images/another.png" in result["image_urls"]
    mock_requests_get.assert_called_once_with(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }, timeout=10)

@patch('arbitrage_os.discovery.scraper.requests.get')
def test_scrape_url_empty_content(mock_requests_get):
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = MOCK_HTML_EMPTY.encode('utf-8')
    mock_response.raise_for_status.return_value = None
    mock_requests_get.return_value = mock_response

    url = "http://example.com/empty"

    # Act
    result = scrape_url(url)

    # Assert
    assert "text" in result
    assert "image_urls" in result
    assert result["text"] == ""
    assert result["image_urls"] == []
    mock_requests_get.assert_called_once_with(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }, timeout=10)

@patch('arbitrage_os.discovery.scraper.requests.get')
def test_scrape_url_network_error(mock_requests_get):
    # Arrange
    mock_requests_get.side_effect = requests.exceptions.RequestException("Network error")

    url = "http://example.com/error"

    # Act
    result = scrape_url(url)

    # Assert
    assert "text" in result
    assert "image_urls" in result
    assert result["text"] == ""
    assert result["image_urls"] == []
    mock_requests_get.assert_called_once_with(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }, timeout=10)

@patch('arbitrage_os.discovery.scraper.requests.get')
def test_scrape_url_relative_image_urls(mock_requests_get):
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = MOCK_HTML_SUCCESS.encode('utf-8')
    mock_response.raise_for_status.return_value = None
    mock_requests_get.return_value = mock_response

    url = "http://example.com/test/page.html"

    # Act
    result = scrape_url(url)

    # Assert
    assert "http://example.com/images/test.jpg" in result["image_urls"]
    assert "http://example.com/images/another.png" in result["image_urls"]
    mock_requests_get.assert_called_once_with(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }, timeout=10)

