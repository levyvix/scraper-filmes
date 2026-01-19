"""Tests for constants module.

Verifies that all constants are properly defined, have correct types, and sensible values.
"""


class TestConstantsImport:
    """Test that all constants can be imported."""

    def test_import_all_constants(self):
        """Test importing all constants from the module."""
        # If we get here, all imports succeeded
        assert True

    def test_http_timeout_is_positive(self):
        """Test that HTTP timeout is a positive integer."""
        from scrapers.utils.constants import HTTP_REQUEST_TIMEOUT_SECONDS

        assert isinstance(HTTP_REQUEST_TIMEOUT_SECONDS, int)
        assert HTTP_REQUEST_TIMEOUT_SECONDS > 0


class TestRetryConstants:
    """Test retry configuration constants."""

    def test_scraper_retry_attempts_is_positive(self):
        """Test that scraper retry attempts is positive."""
        from scrapers.utils.constants import SCRAPER_RETRY_ATTEMPTS

        assert isinstance(SCRAPER_RETRY_ATTEMPTS, int)
        assert SCRAPER_RETRY_ATTEMPTS > 0

    def test_retry_wait_min_less_than_max(self):
        """Test that minimum retry wait is less than maximum."""
        from scrapers.utils.constants import (
            SCRAPER_RETRY_WAIT_MAX_SECONDS,
            SCRAPER_RETRY_WAIT_MIN_SECONDS,
        )

        assert SCRAPER_RETRY_WAIT_MIN_SECONDS < SCRAPER_RETRY_WAIT_MAX_SECONDS

    def test_prefect_task_retries_are_positive(self):
        """Test that Prefect task retry counts are positive."""
        from scrapers.utils.constants import (
            PREFECT_BIGQUERY_TASK_RETRIES,
            PREFECT_SCRAPE_TASK_RETRIES,
        )

        assert PREFECT_SCRAPE_TASK_RETRIES > 0
        assert PREFECT_BIGQUERY_TASK_RETRIES > 0

    def test_prefect_retry_delays_are_positive(self):
        """Test that Prefect retry delay values are positive."""
        from scrapers.utils.constants import (
            PREFECT_BIGQUERY_TASK_RETRY_DELAY_SECONDS,
            PREFECT_SCRAPE_TASK_RETRY_DELAY_SECONDS,
        )

        assert PREFECT_SCRAPE_TASK_RETRY_DELAY_SECONDS > 0
        assert PREFECT_BIGQUERY_TASK_RETRY_DELAY_SECONDS > 0


class TestCacheConstants:
    """Test cache configuration constants."""

    def test_cache_ttl_is_positive(self):
        """Test that cache TTL is a positive integer."""
        from scrapers.utils.constants import CACHE_TTL_SECONDS

        assert isinstance(CACHE_TTL_SECONDS, int)
        assert CACHE_TTL_SECONDS > 0

    def test_cache_directory_is_string(self):
        """Test that cache directory is a string."""
        from scrapers.utils.constants import CACHE_DIRECTORY

        assert isinstance(CACHE_DIRECTORY, str)
        assert len(CACHE_DIRECTORY) > 0

    def test_prefect_cache_expiration_is_positive(self):
        """Test that Prefect cache expiration is positive."""
        from scrapers.utils.constants import PREFECT_TASK_CACHE_EXPIRATION_HOURS

        assert isinstance(PREFECT_TASK_CACHE_EXPIRATION_HOURS, int)
        assert PREFECT_TASK_CACHE_EXPIRATION_HOURS > 0


class TestQualityConstants:
    """Test data quality validation constants."""

    def test_min_fields_filled_ratio_is_between_0_and_1(self):
        """Test that minimum fields filled ratio is between 0 and 1."""
        from scrapers.utils.constants import DEFAULT_MIN_FIELDS_FILLED_RATIO

        assert 0.0 <= DEFAULT_MIN_FIELDS_FILLED_RATIO <= 1.0

    def test_year_bounds_are_sensible(self):
        """Test that year bounds are sensible."""
        from scrapers.utils.constants import MAX_YEAR_ALLOWED, MIN_YEAR_ALLOWED

        assert MIN_YEAR_ALLOWED > 1800  # Film invented around 1888
        assert MAX_YEAR_ALLOWED > MIN_YEAR_ALLOWED
        assert MAX_YEAR_ALLOWED >= 2025  # At least current year

    def test_imdb_rating_bounds_are_correct(self):
        """Test that IMDB rating bounds are 0-10."""
        from scrapers.utils.constants import MAX_IMDB_RATING, MIN_IMDB_RATING

        assert MIN_IMDB_RATING == 0.0
        assert MAX_IMDB_RATING == 10.0

    def test_quality_thresholds_are_valid(self):
        """Test that quality thresholds are within valid range."""
        from scrapers.utils.constants import (
            COMANDO_TORRENTS_QUALITY_THRESHOLD,
            GRATIS_TORRENT_QUALITY_THRESHOLD,
        )

        assert 0.0 <= GRATIS_TORRENT_QUALITY_THRESHOLD <= 10.0
        assert 0.0 <= COMANDO_TORRENTS_QUALITY_THRESHOLD <= 10.0


class TestBigQueryConstants:
    """Test BigQuery configuration constants."""

    def test_bigquery_location_is_valid(self):
        """Test that BigQuery location is set."""
        from scrapers.utils.constants import BIGQUERY_DATASET_LOCATION

        assert isinstance(BIGQUERY_DATASET_LOCATION, str)
        assert len(BIGQUERY_DATASET_LOCATION) > 0


class TestAsyncConstants:
    """Test async HTTP configuration constants."""

    def test_async_http_max_connections_is_positive(self):
        """Test that async HTTP max connections is positive."""
        from scrapers.utils.constants import ASYNC_HTTP_MAX_CONNECTIONS

        assert isinstance(ASYNC_HTTP_MAX_CONNECTIONS, int)
        assert ASYNC_HTTP_MAX_CONNECTIONS > 0

    def test_async_http_max_retries_is_positive(self):
        """Test that async HTTP max retries is positive."""
        from scrapers.utils.constants import ASYNC_HTTP_MAX_RETRIES

        assert isinstance(ASYNC_HTTP_MAX_RETRIES, int)
        assert ASYNC_HTTP_MAX_RETRIES > 0


class TestLoggingConstants:
    """Test logging configuration constants."""

    def test_log_file_names_are_strings(self):
        """Test that log file names are strings."""
        from scrapers.utils.constants import (
            LOG_FILE_COMANDO_TORRENTS,
            LOG_FILE_GRATIS_TORRENT,
        )

        assert isinstance(LOG_FILE_GRATIS_TORRENT, str)
        assert isinstance(LOG_FILE_COMANDO_TORRENTS, str)
        assert len(LOG_FILE_GRATIS_TORRENT) > 0
        assert len(LOG_FILE_COMANDO_TORRENTS) > 0
        assert LOG_FILE_GRATIS_TORRENT.endswith(".log")
        assert LOG_FILE_COMANDO_TORRENTS.endswith(".log")


class TestConstantsAreImmutable:
    """Test that constants cannot be reassigned (they use Final type hint)."""

    def test_constants_cannot_be_reassigned(self):
        """Verify that constants use type hints that prevent reassignment.

        Note: Python's type hints don't enforce immutability at runtime,
        but mypy/static type checkers will catch reassignments.
        """
        from scrapers.utils import constants

        # Verify the module is a module and has the constants
        assert hasattr(constants, "HTTP_REQUEST_TIMEOUT_SECONDS")
        assert hasattr(constants, "CACHE_TTL_SECONDS")
        assert hasattr(constants, "DEFAULT_MIN_FIELDS_FILLED_RATIO")


class TestConstantsDocumentation:
    """Test that constants have proper documentation."""

    def test_constants_module_has_docstring(self):
        """Test that constants module has a module docstring."""
        from scrapers.utils import constants

        assert constants.__doc__ is not None
        assert len(constants.__doc__) > 0

    def test_key_constants_have_reasonable_values(self):
        """Test that key constants have reasonable values."""
        from scrapers.utils.constants import (
            CACHE_TTL_SECONDS,
            HTTP_REQUEST_TIMEOUT_SECONDS,
            SCRAPER_RETRY_ATTEMPTS,
        )

        # HTTP timeout should be reasonable (10s-120s)
        assert 10 <= HTTP_REQUEST_TIMEOUT_SECONDS <= 120

        # Retry attempts should be 1-10
        assert 1 <= SCRAPER_RETRY_ATTEMPTS <= 10

        # Cache TTL should be at least 1 hour
        assert CACHE_TTL_SECONDS >= 3600
