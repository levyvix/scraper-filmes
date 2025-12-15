"""Tests for comando_torrents Prefect flow."""

import pytest
from unittest.mock import patch, MagicMock

# Check if scrapling is available
pytest.importorskip("scrapling", reason="scrapling and camoufox are optional dependencies")

from scrapers.comando_torrents.flow import (
    scrape_movies_task,
    save_to_json_task,
    comando_torrents_flow,
)
from scrapers.utils.models import Movie


class TestScrapeMoviesTask:
    """Tests for scrape_movies_task."""

    @patch("scrapers.comando_torrents.flow.parse_detail")
    @patch("scrapers.comando_torrents.flow.get_movie_links")
    def test_scrape_movies_task_structure(self, mock_get_links, mock_parse):
        """Test that scrape_movies_task is properly configured."""
        # Verify task properties
        assert scrape_movies_task.name == "scrape-comando-movies"
        assert scrape_movies_task.retries == 2

    @patch("scrapers.comando_torrents.flow.parse_detail")
    @patch("scrapers.comando_torrents.flow.get_movie_links")
    def test_scrape_movies_task_with_no_links(self, mock_get_links, mock_parse):
        """Test scraping when no movie links found."""
        # Setup mock
        mock_get_links.return_value = []

        # Call function directly
        result = scrape_movies_task("https://test.com/empty")

        # Verify returns empty list
        assert result == []


class TestSaveToJsonTask:
    """Tests for save_to_json_task."""

    def test_save_to_json_task_structure(self):
        """Test that save_to_json_task is properly configured."""
        # Verify task properties
        assert save_to_json_task.name == "save-comando-movies"

    def test_save_to_json_task_can_be_called(self):
        """Test that save_to_json_task can be imported and called."""
        # The function should be callable
        # We test import and callable status here
        assert callable(save_to_json_task)


class TestComandoTorrentsFlow:
    """Tests for main comando_torrents_flow."""

    def test_comando_torrents_flow_structure(self):
        """Test that comando_torrents_flow is properly configured."""
        # Verify flow properties
        assert comando_torrents_flow.name == "comando-torrents-scraper"

    @patch("scrapers.comando_torrents.flow.ComandoTorrentsConfig")
    @patch("scrapers.comando_torrents.flow.save_to_json_task")
    @patch("scrapers.comando_torrents.flow.scrape_movies_task")
    def test_comando_torrents_flow_structure_with_mocks(self, mock_scrape, mock_save, mock_config_class):
        """Test flow execution with mocks."""
        # Setup
        mock_config = MagicMock()
        mock_config.URL_BASE = "https://test.com/movies"
        mock_config_class.return_value = mock_config

        # Mock scrape returns a movie
        movie = Movie(
            titulo_dublado="Movie",
            titulo_original="Original",
            imdb=8.0,
            ano=2020,
            link="https://test.com/movie",
        )
        mock_scrape.return_value = [movie]

        # Call function
        comando_torrents_flow()

        # Verify tasks were called
        mock_scrape.assert_called_once()

    @patch("scrapers.comando_torrents.flow.ComandoTorrentsConfig")
    @patch("scrapers.comando_torrents.flow.scrape_movies_task")
    def test_comando_torrents_flow_with_no_movies(self, mock_scrape, mock_config_class):
        """Test flow behavior when no movies are scraped."""
        # Setup
        mock_config = MagicMock()
        mock_config.URL_BASE = "https://test.com/movies"
        mock_config_class.return_value = mock_config
        mock_scrape.return_value = []

        # Call function
        comando_torrents_flow()

        # Verify scrape was called
        mock_scrape.assert_called_once()


class TestFlowStructure:
    """Tests for Prefect flow structure."""

    def test_scrape_movies_task_has_correct_name(self):
        """Test that scrape task has correct Prefect name."""
        assert scrape_movies_task.name == "scrape-comando-movies"

    def test_save_to_json_task_has_correct_name(self):
        """Test that save task has correct Prefect name."""
        assert save_to_json_task.name == "save-comando-movies"

    def test_comando_torrents_flow_has_correct_name(self):
        """Test that main flow has correct Prefect name."""
        assert comando_torrents_flow.name == "comando-torrents-scraper"

    def test_scrape_movies_task_has_retries(self):
        """Test that scrape task has retry configuration."""
        assert scrape_movies_task.retries == 2
