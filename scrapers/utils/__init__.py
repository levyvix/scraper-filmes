"""Shared utilities for movie scrapers.

This package contains common parsing functions, data validation, exception types,
and configuration constants used across all scraper modules.

Main exports:
    - Movie: Base Pydantic model for movie data
    - DataQualityChecker: Validates movie data quality
    - parse_rating, parse_year, parse_int: Parsing utility functions
    - Exception types: ScraperException, FetchException, ParsingException, etc.
    - Constants: HTTP timeouts, retry policies, validation thresholds
"""

from scrapers.utils.constants import (
    ASYNC_HTTP_MAX_CONNECTIONS,
    ASYNC_HTTP_MAX_RETRIES,
    BIGQUERY_DATASET_LOCATION,
    CACHE_DIRECTORY,
    CACHE_TTL_SECONDS,
    COMANDO_TORRENTS_QUALITY_THRESHOLD,
    DEFAULT_MIN_FIELDS_FILLED_RATIO,
    GRATIS_TORRENT_QUALITY_THRESHOLD,
    HTTP_REQUEST_TIMEOUT_SECONDS,
    LOG_FILE_COMANDO_TORRENTS,
    LOG_FILE_GRATIS_TORRENT,
    MAX_IMDB_RATING,
    MAX_YEAR_ALLOWED,
    MIN_IMDB_RATING,
    MIN_YEAR_ALLOWED,
    PREFECT_BIGQUERY_TASK_RETRIES,
    PREFECT_BIGQUERY_TASK_RETRY_DELAY_SECONDS,
    PREFECT_SCRAPE_TASK_RETRIES,
    PREFECT_SCRAPE_TASK_RETRY_DELAY_SECONDS,
    PREFECT_TASK_CACHE_EXPIRATION_HOURS,
    SCRAPER_RETRY_ATTEMPTS,
    SCRAPER_RETRY_MULTIPLIER,
    SCRAPER_RETRY_WAIT_MAX_SECONDS,
    SCRAPER_RETRY_WAIT_MIN_SECONDS,
)
from scrapers.utils.data_quality import DataQualityChecker
from scrapers.utils.exceptions import (
    BigQueryException,
    FetchException,
    ParsingException,
    ScraperException,
    ValidationException,
)
from scrapers.utils.models import Movie
from scrapers.utils.parse_utils import parse_int, parse_rating, parse_year

__all__ = [
    # Models
    "Movie",
    # Quality Checking
    "DataQualityChecker",
    # Parsing Functions
    "parse_rating",
    "parse_year",
    "parse_int",
    # Exception Types
    "ScraperException",
    "FetchException",
    "ParsingException",
    "ValidationException",
    "BigQueryException",
    # HTTP Configuration
    "HTTP_REQUEST_TIMEOUT_SECONDS",
    # Retry Configuration
    "SCRAPER_RETRY_ATTEMPTS",
    "SCRAPER_RETRY_WAIT_MIN_SECONDS",
    "SCRAPER_RETRY_WAIT_MAX_SECONDS",
    "SCRAPER_RETRY_MULTIPLIER",
    "PREFECT_SCRAPE_TASK_RETRIES",
    "PREFECT_SCRAPE_TASK_RETRY_DELAY_SECONDS",
    "PREFECT_BIGQUERY_TASK_RETRIES",
    "PREFECT_BIGQUERY_TASK_RETRY_DELAY_SECONDS",
    # Cache Configuration
    "CACHE_TTL_SECONDS",
    "CACHE_DIRECTORY",
    "PREFECT_TASK_CACHE_EXPIRATION_HOURS",
    # Quality Thresholds
    "DEFAULT_MIN_FIELDS_FILLED_RATIO",
    "MIN_YEAR_ALLOWED",
    "MAX_YEAR_ALLOWED",
    "MIN_IMDB_RATING",
    "MAX_IMDB_RATING",
    "GRATIS_TORRENT_QUALITY_THRESHOLD",
    "COMANDO_TORRENTS_QUALITY_THRESHOLD",
    # BigQuery
    "BIGQUERY_DATASET_LOCATION",
    # Async Configuration
    "ASYNC_HTTP_MAX_CONNECTIONS",
    "ASYNC_HTTP_MAX_RETRIES",
    # Logging
    "LOG_FILE_GRATIS_TORRENT",
    "LOG_FILE_COMANDO_TORRENTS",
]
