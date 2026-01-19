"""Tests for comando_torrents scraper module."""

from unittest.mock import Mock, patch

import pytest
from scrapling.parser import Adaptor

from scrapers.comando_torrents.scraper import (
    fetch_page,
    get_movie_links,
)
from scrapers.utils.exceptions import FetchException


class TestFetchPage:
    """Tests for fetch_page function."""

    @patch("scrapers.comando_torrents.scraper.fetch_page_html")
    def test_fetch_page_success(self, mock_fetch_html):
        """Test successful page fetch and Adaptor creation."""
        # Setup mock
        mock_fetch_html.return_value = (
            "<html><body>Test</body></html>",
            "https://test.com",
        )

        # Call function
        result = fetch_page("https://test.com")

        # Verify result is Adaptor
        assert isinstance(result, Adaptor)
        mock_fetch_html.assert_called_once_with("https://test.com")

    @patch("scrapers.comando_torrents.scraper.fetch_page_html")
    def test_fetch_page_with_fetch_exception(self, mock_fetch_html):
        """Test fetch_page propagates FetchException."""
        # Setup mock to raise exception
        mock_fetch_html.side_effect = FetchException("Fetch failed")

        # Verify exception is propagated
        with pytest.raises(FetchException):
            fetch_page("https://test.com")

    @patch("scrapers.comando_torrents.scraper.fetch_page_html")
    def test_fetch_page_adaptor_has_correct_url(self, mock_fetch_html):
        """Test that Adaptor is created with correct URL."""
        # Setup mock
        mock_fetch_html.return_value = (
            "<html>Content</html>",
            "https://example.com/page",
        )

        # Call function
        result = fetch_page("https://example.com/page")

        # Verify Adaptor has correct URL
        assert result.url == "https://example.com/page"

    @patch("scrapers.comando_torrents.scraper.fetch_page_html")
    def test_fetch_page_with_unicode_content(self, mock_fetch_html):
        """Test fetch_page handles unicode HTML content."""
        # Setup mock with unicode content
        html_content = "<html><body>Película Açúcar</body></html>"
        mock_fetch_html.return_value = (html_content, "https://test.com")

        # Call function
        result = fetch_page("https://test.com")

        # Verify Adaptor was created successfully
        assert isinstance(result, Adaptor)


class TestGetMovieLinks:
    """Tests for get_movie_links function."""

    @patch("scrapers.comando_torrents.scraper.fetch_page")
    def test_get_movie_links_success(self, mock_fetch):
        """Test successful extraction of movie links."""
        # Setup mock page with CSS selector results
        mock_page = Mock()
        mock_page.css.return_value = [
            "https://test.com/movie1",
            "https://test.com/movie2",
            "https://test.com/movie3",
        ]
        mock_fetch.return_value = mock_page

        # Call function
        links = get_movie_links("https://test.com/movies")

        # Verify
        assert len(links) == 3
        assert links[0] == "https://test.com/movie1"
        assert links[1] == "https://test.com/movie2"
        assert links[2] == "https://test.com/movie3"
        mock_page.css.assert_called_once_with("article > header > h2 > a::attr(href)")

    @patch("scrapers.comando_torrents.scraper.fetch_page")
    @patch("scrapers.comando_torrents.scraper.logger")
    def test_get_movie_links_fetch_exception(self, mock_logger, mock_fetch):
        """Test get_movie_links handles FetchException."""
        # Setup mock to raise FetchException
        mock_fetch.side_effect = FetchException("Failed to fetch")

        # Call function
        links = get_movie_links("https://test.com/movies")

        # Verify returns empty list
        assert links == []
        assert mock_logger.error.called

    @patch("scrapers.comando_torrents.scraper.fetch_page")
    @patch("scrapers.comando_torrents.scraper.logger")
    def test_get_movie_links_unexpected_exception(self, mock_logger, mock_fetch):
        """Test get_movie_links handles unexpected exceptions."""
        # Setup mock to raise unexpected error
        mock_fetch.side_effect = RuntimeError("Unexpected error")

        # Call function
        links = get_movie_links("https://test.com/movies")

        # Verify returns empty list
        assert links == []
        assert mock_logger.error.called

    @patch("scrapers.comando_torrents.scraper.fetch_page")
    def test_get_movie_links_empty_result(self, mock_fetch):
        """Test get_movie_links with empty results."""
        # Setup mock page with no links
        mock_page = Mock()
        mock_page.css.return_value = []
        mock_fetch.return_value = mock_page

        # Call function
        links = get_movie_links("https://test.com/movies")

        # Verify returns empty list
        assert links == []

    @patch("scrapers.comando_torrents.scraper.fetch_page")
    def test_get_movie_links_converts_to_strings(self, mock_fetch):
        """Test that link results are converted to strings."""
        # Setup mock with non-string objects
        mock_page = Mock()
        mock_obj1 = Mock()
        mock_obj1.__str__ = Mock(return_value="https://test.com/movie1")
        mock_obj2 = Mock()
        mock_obj2.__str__ = Mock(return_value="https://test.com/movie2")
        mock_page.css.return_value = [mock_obj1, mock_obj2]
        mock_fetch.return_value = mock_page

        # Call function
        links = get_movie_links("https://test.com/movies")

        # Verify objects were converted to strings
        assert len(links) == 2
        assert all(isinstance(link, str) for link in links)

    @patch("scrapers.comando_torrents.scraper.fetch_page")
    def test_get_movie_links_selector_is_correct(self, mock_fetch):
        """Test that correct CSS selector is used."""
        # Setup mock
        mock_page = Mock()
        mock_page.css.return_value = []
        mock_fetch.return_value = mock_page

        # Call function
        get_movie_links("https://test.com/movies")

        # Verify correct selector was used
        mock_page.css.assert_called_once_with("article > header > h2 > a::attr(href)")

    @patch("scrapers.comando_torrents.scraper.fetch_page")
    def test_get_movie_links_with_single_result(self, mock_fetch):
        """Test with single movie link result."""
        # Setup mock
        mock_page = Mock()
        mock_page.css.return_value = ["https://test.com/movie1"]
        mock_fetch.return_value = mock_page

        # Call function
        links = get_movie_links("https://test.com/movies")

        # Verify
        assert len(links) == 1
        assert links[0] == "https://test.com/movie1"

    @patch("scrapers.comando_torrents.scraper.fetch_page")
    def test_get_movie_links_with_many_results(self, mock_fetch):
        """Test with many movie links (stress test)."""
        # Setup mock with many links
        mock_page = Mock()
        num_movies = 100
        movie_links = [f"https://test.com/movie{i}" for i in range(num_movies)]
        mock_page.css.return_value = movie_links
        mock_fetch.return_value = mock_page

        # Call function
        links = get_movie_links("https://test.com/movies")

        # Verify
        assert len(links) == num_movies
        assert links[0] == "https://test.com/movie0"
        assert links[-1] == f"https://test.com/movie{num_movies - 1}"
