import pytest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
import requests

from scrapers.gratis_torrent.http_client import fetch_page
from scrapers.utils.exceptions import FetchException


class MockResponse:
    """A mock class to simulate requests.Response objects."""

    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code
        self.response = MagicMock(status_code=status_code)  # For HTTPError

    def raise_for_status(self):
        if self.status_code >= 400:
            http_error = requests.HTTPError(
                f"{self.status_code} Client Error: Mocked Error", response=self
            )
            raise http_error


@patch("requests.get")
def test_fetch_page_success(mock_get):
    mock_get.return_value = MockResponse("<html><body><h1>Test</h1></body></html>", 200)

    soup = fetch_page("http://example.com", timeout=10)  # Pass timeout explicitly
    mock_get.assert_called_once_with("http://example.com", timeout=10)
    assert isinstance(soup, BeautifulSoup)
    assert soup.find("h1").text == "Test"


@patch("requests.get")
def test_fetch_page_timeout(mock_get):
    mock_get.side_effect = requests.Timeout("Request timed out")

    with pytest.raises(FetchException, match="Request timeout for http://example.com"):
        fetch_page("http://example.com", timeout=10)  # Pass timeout explicitly
    mock_get.assert_called_once_with("http://example.com", timeout=10)


@patch("requests.get")
def test_fetch_page_http_error(mock_get):
    mock_response = MockResponse("", 404)
    mock_get.side_effect = (
        lambda *args, **kwargs: mock_response.raise_for_status()
    )  # Wrap in lambda to ignore args/kwargs

    with pytest.raises(FetchException, match="HTTP 404 for http://example.com"):
        fetch_page("http://example.com", timeout=10)  # Pass timeout explicitly
    mock_get.assert_called_once_with("http://example.com", timeout=10)


@patch("requests.get")
def test_fetch_page_connection_error(mock_get):
    mock_get.side_effect = requests.ConnectionError("Max retries exceeded")

    with pytest.raises(FetchException, match="Request failed for http://example.com"):
        fetch_page("http://example.com", timeout=10)  # Pass timeout explicitly
    mock_get.assert_called_once_with("http://example.com", timeout=10)


# The collect_movie_links is already tested in test_http_client.py
# So no need to re-test it here.
