"""Tests for http_client module."""

from unittest.mock import Mock, patch

import requests
from bs4 import BeautifulSoup

from src.scrapers.gratis_torrent.http_client import collect_movie_links, fetch_page


class TestFetchPage:
    """Tests for fetch_page function."""

    @patch("src.scrapers.gratis_torrent.http_client.requests.get")
    def test_fetch_page_success(self, mock_get):
        """Test successfully fetching a page."""
        mock_response = Mock()
        mock_response.text = "<html><body>Test</body></html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = fetch_page("https://example.com")

        assert result is not None
        assert isinstance(result, BeautifulSoup)
        mock_get.assert_called_once_with("https://example.com", timeout=40)

    @patch("src.scrapers.gratis_torrent.http_client.requests.get")
    def test_fetch_page_timeout(self, mock_get):
        """Test handling timeout error."""
        mock_get.side_effect = requests.Timeout("Timeout error")

        result = fetch_page("https://example.com")

        assert result is None

    @patch("src.scrapers.gratis_torrent.http_client.requests.get")
    def test_fetch_page_http_error(self, mock_get):
        """Test handling HTTP error."""
        mock_get.side_effect = requests.HTTPError("404 Not Found")

        result = fetch_page("https://example.com")

        assert result is None

    @patch("src.scrapers.gratis_torrent.http_client.requests.get")
    def test_fetch_page_custom_timeout(self, mock_get):
        """Test fetching page with custom timeout."""
        mock_response = Mock()
        mock_response.text = "<html><body>Test</body></html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        fetch_page("https://example.com", timeout=30)

        mock_get.assert_called_once_with("https://example.com", timeout=30)


class TestCollectMovieLinks:
    """Tests for collect_movie_links function."""

    def test_collect_links_multiple(self):
        """Test collecting multiple movie links."""
        html = """
        <html>
            <div id="capas_pequenas">
                <div><a href="https://example.com/movie1">Movie 1</a></div>
                <div><a href="https://example.com/movie2">Movie 2</a></div>
                <div><a href="https://example.com/movie3">Movie 3</a></div>
            </div>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")

        links = collect_movie_links(soup)

        assert len(links) == 3
        assert "https://example.com/movie1" in links
        assert "https://example.com/movie2" in links
        assert "https://example.com/movie3" in links

    def test_collect_links_with_duplicates(self):
        """Test collecting links with duplicates."""
        html = """
        <html>
            <div id="capas_pequenas">
                <div><a href="https://example.com/movie1">Movie 1</a></div>
                <div><a href="https://example.com/movie2">Movie 2</a></div>
                <div><a href="https://example.com/movie1">Movie 1 Again</a></div>
            </div>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")

        links = collect_movie_links(soup)

        assert len(links) == 2
        assert "https://example.com/movie1" in links
        assert "https://example.com/movie2" in links

    def test_collect_links_empty(self):
        """Test collecting from page with no links."""
        html = """
        <html>
            <div id="capas_pequenas">
            </div>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")

        links = collect_movie_links(soup)

        assert len(links) == 0

    def test_collect_links_no_href(self):
        """Test collecting links when anchor has no href."""
        html = """
        <html>
            <div id="capas_pequenas">
                <div><a>Movie without link</a></div>
                <div><a href="https://example.com/movie1">Movie 1</a></div>
            </div>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")

        links = collect_movie_links(soup)

        assert len(links) == 1
        assert "https://example.com/movie1" in links
