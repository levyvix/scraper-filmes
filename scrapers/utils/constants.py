"""Centralized configuration constants for all scrapers.

This module contains hardcoded values like timeouts, retry policies, and validation
thresholds that are shared across the scraper modules.

Values are organized by category (HTTP, Retries, Validation, BigQuery, Quality).
"""

from typing import Final

# ============================================================================
# HTTP Configuration Constants
# ============================================================================

HTTP_REQUEST_TIMEOUT_SECONDS: Final[int] = 40
"""Timeout for HTTP requests in seconds. Prevents hanging on slow servers."""

# ============================================================================
# Retry Policy Constants
# ============================================================================

SCRAPER_RETRY_ATTEMPTS: Final[int] = 3
"""Number of retry attempts for scraping individual movie pages."""

SCRAPER_RETRY_WAIT_MIN_SECONDS: Final[int] = 4
"""Minimum wait time between retry attempts (exponential backoff)."""

SCRAPER_RETRY_WAIT_MAX_SECONDS: Final[int] = 10
"""Maximum wait time between retry attempts (exponential backoff)."""

SCRAPER_RETRY_MULTIPLIER: Final[int] = 1
"""Multiplier for exponential backoff in retry policy."""

PREFECT_SCRAPE_TASK_RETRIES: Final[int] = 2
"""Number of retries for Prefect scraping task."""

PREFECT_SCRAPE_TASK_RETRY_DELAY_SECONDS: Final[int] = 30
"""Delay in seconds before retrying scrape task."""

PREFECT_BIGQUERY_TASK_RETRIES: Final[int] = 3
"""Number of retries for Prefect BigQuery load task."""

PREFECT_BIGQUERY_TASK_RETRY_DELAY_SECONDS: Final[int] = 60
"""Delay in seconds before retrying BigQuery load task."""

# ============================================================================
# Cache Configuration Constants
# ============================================================================

CACHE_TTL_SECONDS: Final[int] = 3600
"""Cache time-to-live in seconds (1 hour). Movies are re-scraped after this."""

CACHE_DIRECTORY: Final[str] = "movie_cache"
"""Local directory for DiskCache storage."""

PREFECT_TASK_CACHE_EXPIRATION_HOURS: Final[int] = 1
"""Prefect task cache expiration in hours."""

# ============================================================================
# Data Quality Constants
# ============================================================================

DEFAULT_MIN_FIELDS_FILLED_RATIO: Final[float] = 0.7
"""Minimum ratio of fields that must be filled for a movie to pass quality checks."""

MIN_YEAR_ALLOWED: Final[int] = 1888
"""Earliest year allowed for movies in the dataset. Historical minimum."""

MAX_YEAR_ALLOWED: Final[int] = 2030
"""Latest year allowed for movies (buffer for future releases)."""

MIN_IMDB_RATING: Final[float] = 0.0
"""Minimum IMDB rating (0.0 for no lower bound, movies often have no rating)."""

MAX_IMDB_RATING: Final[float] = 10.0
"""Maximum IMDB rating (scale is 0-10)."""

# ============================================================================
# Quality Threshold Constants (Scraper-Specific)
# ============================================================================

GRATIS_TORRENT_QUALITY_THRESHOLD: Final[float] = 7.0
"""Minimum quality score for GratisTorrent scraper (0-10 scale)."""

COMANDO_TORRENTS_QUALITY_THRESHOLD: Final[float] = 7.0
"""Minimum quality score for Comando Torrents scraper (0-10 scale)."""

# ============================================================================
# BigQuery Configuration Constants
# ============================================================================

BIGQUERY_DATASET_LOCATION: Final[str] = "US"
"""Default location for BigQuery dataset (us-central1)."""

# ============================================================================
# Async HTTP Constants (for future async scraper)
# ============================================================================

ASYNC_HTTP_MAX_CONNECTIONS: Final[int] = 10
"""Maximum concurrent HTTP connections for async scraper."""

ASYNC_HTTP_MAX_RETRIES: Final[int] = 3
"""Maximum retries for individual async requests."""

# ============================================================================
# Logging Constants
# ============================================================================

LOG_FILE_GRATIS_TORRENT: Final[str] = "gratis_torrent.log"
"""Log file name for GratisTorrent scraper."""

LOG_FILE_COMANDO_TORRENTS: Final[str] = "comando_torrents.log"
"""Log file name for Comando Torrents scraper."""
