"""Tests for scrapers.utils package public API."""


class TestUtilsPackageAPI:
    """Test that public API is properly exported from scrapers.utils."""

    def test_import_movie_model(self):
        """Test that Movie model can be imported from utils."""
        from scrapers.utils import Movie

        assert Movie is not None

    def test_import_data_quality_checker(self):
        """Test that DataQualityChecker can be imported from utils."""
        from scrapers.utils import DataQualityChecker

        assert DataQualityChecker is not None

    def test_import_parse_functions(self):
        """Test that parsing functions can be imported from utils."""
        from scrapers.utils import parse_int, parse_rating, parse_year

        assert callable(parse_rating)
        assert callable(parse_year)
        assert callable(parse_int)

    def test_import_exception_classes(self):
        """Test that exception classes can be imported from utils."""
        from scrapers.utils import (
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

    def test_import_constants(self):
        """Test that constants can be imported from utils."""
        from scrapers.utils import (
            CACHE_TTL_SECONDS,
            DEFAULT_MIN_FIELDS_FILLED_RATIO,
            HTTP_REQUEST_TIMEOUT_SECONDS,
        )

        assert HTTP_REQUEST_TIMEOUT_SECONDS is not None
        assert CACHE_TTL_SECONDS is not None
        assert DEFAULT_MIN_FIELDS_FILLED_RATIO is not None

    def test_all_attribute_exists(self):
        """Test that __all__ is defined in utils package."""
        from scrapers import utils

        assert hasattr(utils, "__all__")
        assert isinstance(utils.__all__, (list, tuple))
        assert len(utils.__all__) > 0
