"""Tests for the root scrapers package public API.

Verifies that all major components can be imported from the root `scrapers` package.
"""


class TestRootPackageAPI:
    """Test that public API is properly exported from scrapers root."""

    def test_import_scrape_gratis_torrent_function(self):
        """Test that scrape_gratis_torrent can be imported from root."""
        from scrapers import scrape_gratis_torrent

        assert callable(scrape_gratis_torrent)

    def test_import_gratis_torrent_config(self):
        """Test that GratisTorrentConfig can be imported from root."""
        from scrapers import GratisTorrentConfig

        assert GratisTorrentConfig is not None

    def test_import_movie_from_root(self):
        """Test that Movie model can be imported from root."""
        from scrapers import Movie

        assert Movie is not None

    def test_import_data_quality_checker(self):
        """Test that DataQualityChecker can be imported from root."""
        from scrapers import DataQualityChecker

        assert DataQualityChecker is not None

    def test_import_scraper_exceptions(self):
        """Test that exception classes can be imported from root."""
        from scrapers import (
            BigQueryException,
            FetchException,
            ParsingException,
            ScraperException,
            ValidationException,
        )

        assert ScraperException is not None
        assert FetchException is not None
        assert ParsingException is not None
        assert ValidationException is not None
        assert BigQueryException is not None

    def test_all_attribute_exists(self):
        """Test that __all__ is defined in root package."""
        import scrapers

        assert hasattr(scrapers, "__all__")
        assert isinstance(scrapers.__all__, (list, tuple))
        assert len(scrapers.__all__) > 0
