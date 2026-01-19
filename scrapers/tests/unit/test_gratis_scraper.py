from unittest.mock import MagicMock, patch

import pytest
from bs4 import BeautifulSoup

from scrapers.gratis_torrent.models import Movie
from scrapers.gratis_torrent.scraper import (
    scrape_all_movies,
    scrape_movie_details,
    scrape_movie_links,
)
from scrapers.utils.data_quality import DataQualityChecker  # Import for mocking
from scrapers.utils.exceptions import FetchException, ScraperException


# Mock the Config.BASE_URL for testing scrape_movie_links
@pytest.fixture(autouse=True)
def mock_config_base_url():
    with patch("scrapers.gratis_torrent.config.Config.BASE_URL", "http://test.com"):
        yield


class TestScrapeMovieLinks:
    # Patch fetch_page and collect_movie_links where they are USED in scraper.py
    @patch("scrapers.gratis_torrent.scraper.fetch_page")
    @patch("scrapers.gratis_torrent.scraper.collect_movie_links")
    def test_scrape_movie_links_success(self, mock_collect_links, mock_fetch_page):
        mock_fetch_page.return_value = BeautifulSoup("<html></html>", "html.parser")
        mock_collect_links.return_value = ["link1", "link2"]

        links = scrape_movie_links()

        mock_fetch_page.assert_called_once_with("http://test.com")
        mock_collect_links.assert_called_once_with(mock_fetch_page.return_value)
        assert links == ["link1", "link2"]

    @patch("scrapers.gratis_torrent.scraper.fetch_page")
    def test_scrape_movie_links_fetch_exception(
        self, mock_fetch_page, caplog
    ):  # Use caplog fixture
        mock_fetch_page.side_effect = FetchException("Failed to fetch")

        with caplog.at_level("ERROR"):  # Capture logs at ERROR level
            links = scrape_movie_links()

        mock_fetch_page.assert_called_once_with("http://test.com")
        assert "Cannot access http://test.com: Failed to fetch" in caplog.text
        assert links == []


class TestScrapeMovieDetails:
    # Patch fetch_page and parse_movie_page where they are USED in scraper.py
    @patch("scrapers.gratis_torrent.scraper.fetch_page")
    @patch("scrapers.gratis_torrent.scraper.parse_movie_page")
    def test_scrape_movie_details_success(self, mock_parse_movie_page, mock_fetch_page):
        mock_fetch_page.return_value = BeautifulSoup("<html></html>", "html.parser")
        mock_parse_movie_page.return_value = Movie(
            titulo_dublado="Test Movie", link="http://test.com/movie"
        )

        movie = scrape_movie_details("http://test.com/movie")

        mock_fetch_page.assert_called_once_with("http://test.com/movie")
        mock_parse_movie_page.assert_called_once_with(
            mock_fetch_page.return_value, "http://test.com/movie"
        )
        assert movie.titulo_dublado == "Test Movie"

    @patch("scrapers.gratis_torrent.scraper.fetch_page")
    @patch("scrapers.gratis_torrent.scraper.parse_movie_page")
    def test_scrape_movie_details_no_movie_data(
        self, mock_parse_movie_page, mock_fetch_page
    ):
        mock_fetch_page.return_value = BeautifulSoup("<html></html>", "html.parser")
        mock_parse_movie_page.return_value = None

        movie = scrape_movie_details("http://test.com/movie")

        assert movie is None

    @patch("scrapers.gratis_torrent.scraper.fetch_page")
    def test_scrape_movie_details_fetch_exception(
        self, mock_fetch_page, caplog
    ):  # Use caplog fixture
        # Configure mock_fetch_page to raise FetchException for all 3 attempts
        mock_fetch_page.side_effect = [FetchException("Fetch error")] * 3

        with caplog.at_level("ERROR"):
            with pytest.raises(
                ScraperException, match="Failed to fetch http://test.com/movie"
            ):
                scrape_movie_details("http://test.com/movie")

        # Each retry logs "Error fetching..." exactly once per attempt = 3 logs total
        assert len(caplog.records) == 3
        assert "Error fetching http://test.com/movie: Fetch error" in caplog.text
        assert mock_fetch_page.call_count == 3
        mock_fetch_page.assert_called_with("http://test.com/movie")  # Check last call

    @patch("scrapers.gratis_torrent.scraper.fetch_page")
    @patch("scrapers.gratis_torrent.scraper.parse_movie_page")
    def test_scrape_movie_details_generic_exception(
        self, mock_parse_movie_page, mock_fetch_page, caplog
    ):  # Use caplog fixture
        mock_fetch_page.return_value = BeautifulSoup("<html></html>", "html.parser")
        mock_parse_movie_page.side_effect = [Exception("Parsing error")] * 3

        with caplog.at_level("ERROR"):
            with pytest.raises(
                ScraperException, match="Failed to scrape http://test.com/movie"
            ):
                scrape_movie_details("http://test.com/movie")

        # Each retry logs "Error scraping..." exactly once per attempt = 3 logs total
        assert len(caplog.records) == 3
        assert "Error scraping http://test.com/movie: Parsing error" in caplog.text
        assert mock_parse_movie_page.call_count == 3
        mock_parse_movie_page.assert_called_with(
            mock_fetch_page.return_value, "http://test.com/movie"
        )


class TestScrapeAllMovies:
    @patch("scrapers.gratis_torrent.scraper.scrape_movie_links")
    @patch("scrapers.gratis_torrent.scraper.scrape_movie_details")
    @patch(
        "scrapers.gratis_torrent.scraper.DataQualityChecker"
    )  # Patch DataQualityChecker as imported in scraper
    def test_scrape_all_movies_success(
        self, mock_quality_checker_cls, mock_scrape_details, mock_scrape_links, caplog
    ):  # Use caplog fixture
        mock_scrape_links.return_value = ["link1", "link2"]
        mock_scrape_details.side_effect = [
            Movie(titulo_dublado="Movie 1", link="link1"),
            Movie(titulo_dublado="Movie 2", link="link2"),
        ]

        mock_quality_checker = MagicMock(
            spec=DataQualityChecker
        )  # Create a mock instance
        mock_quality_checker.check_movie.return_value = True
        mock_quality_checker.check_batch.return_value = {
            "pass_rate": 1.0,
            "passed_quality": 2,
            "total_movies": 2,
            "issues": [],
        }
        mock_quality_checker_cls.return_value = mock_quality_checker  # Return the mock instance when DataQualityChecker is called

        with caplog.at_level("INFO"):
            movies = scrape_all_movies()

        assert len(movies) == 2
        mock_scrape_links.assert_called_once()
        assert mock_scrape_details.call_count == 2
        assert mock_quality_checker.check_movie.call_count == 2
        assert mock_quality_checker.check_batch.call_count == 1

        # Check specific log messages using caplog.text
        # Note: "Found..." is in scrape_movie_links which is mocked, so it won't appear
        assert "Processing movie 1/2: link1" in caplog.text
        assert "Processing movie 2/2: link2" in caplog.text
        assert "Successfully scraped 2 movies. Failed: 0 out of 2" in caplog.text
        assert "Quality Report: 100.0% pass rate (2/2 movies)" in caplog.text

    @patch("scrapers.gratis_torrent.scraper.scrape_movie_links")
    @patch("scrapers.gratis_torrent.scraper.scrape_movie_details")
    @patch("scrapers.utils.data_quality.DataQualityChecker")
    def test_scrape_all_movies_details_none(
        self, mock_quality_checker_cls, mock_scrape_details, mock_scrape_links, caplog
    ):  # Use caplog fixture
        mock_scrape_links.return_value = ["link1"]
        mock_scrape_details.return_value = None

        mock_quality_checker = MagicMock(spec=DataQualityChecker)
        mock_quality_checker.check_movie.return_value = (
            True  # Not called if movie is None
        )
        mock_quality_checker_cls.return_value = mock_quality_checker

        with caplog.at_level("WARNING"):
            movies = scrape_all_movies()

        assert len(movies) == 0
        assert "Failed to extract info from link1" in caplog.text
        assert "Failed links: ['link1']..." in caplog.text

    @patch("scrapers.gratis_torrent.scraper.scrape_movie_links")
    @patch("scrapers.gratis_torrent.scraper.scrape_movie_details")
    @patch("scrapers.utils.data_quality.DataQualityChecker")
    def test_scrape_all_movies_scraper_exception(
        self, mock_quality_checker_cls, mock_scrape_details, mock_scrape_links, caplog
    ):  # Use caplog fixture
        mock_scrape_links.return_value = ["link1"]
        mock_scrape_details.side_effect = ScraperException("Scrape failed")

        mock_quality_checker = MagicMock(spec=DataQualityChecker)
        mock_quality_checker.check_movie.return_value = True
        mock_quality_checker_cls.return_value = mock_quality_checker

        with caplog.at_level("ERROR"):
            movies = scrape_all_movies()

        assert len(movies) == 0
        assert "Failed to scrape link1 after retries: Scrape failed" in caplog.text

    @patch("scrapers.gratis_torrent.scraper.scrape_movie_links")
    @patch("scrapers.gratis_torrent.scraper.scrape_movie_details")
    @patch("scrapers.gratis_torrent.scraper.DataQualityChecker")
    def test_scrape_all_movies_quality_check_fail(
        self, mock_quality_checker_cls, mock_scrape_details, mock_scrape_links, caplog
    ):  # Use caplog fixture
        mock_scrape_links.return_value = ["link1"]
        mock_scrape_details.return_value = Movie(
            titulo_dublado="Bad Movie", link="link1"
        )

        mock_quality_checker = MagicMock(spec=DataQualityChecker)
        mock_quality_checker.check_movie.return_value = False
        mock_quality_checker_cls.return_value = mock_quality_checker

        with caplog.at_level("WARNING"):
            movies = scrape_all_movies()

        assert len(movies) == 0
        assert "Movie link1 failed quality checks" in caplog.text
        assert "Failed links: ['link1']..." in caplog.text
        assert mock_quality_checker.check_movie.call_count == 1
