"""Prefect flow for GratisTorrent scraper pipeline."""

import json
from typing import Any
from pathlib import Path

from prefect import flow, task
from prefect.cache_policies import INPUTS, TASK_SOURCE
from datetime import timedelta

from scrapers.utils.logging_config import setup_logging
from scrapers.gratis_torrent.bigquery_client import load_movies_to_bigquery, get_gcp_credentials
from scrapers.gratis_torrent.scraper import scrape_all_movies
from scrapers.gratis_torrent.config import Config

# Initialize logging configuration
logger = setup_logging(level="INFO", log_file="gratis_torrent.log")


@task(name="validate-credentials", log_prints=True)
def validate_credentials_task() -> bool:
    """
    Task to validate GCP credentials at flow startup.

    Detects which credential method is configured and validates it can be loaded.

    Returns:
        True if credentials are valid

    Raises:
        ValueError: If credentials cannot be loaded
    """
    logger.info("Validating GCP credentials...")
    try:
        get_gcp_credentials()
        logger.success(f"GCP credentials validated (method: {Config.GCP_CREDENTIALS_METHOD})")
        return True
    except Exception as e:
        logger.error(f"Failed to validate GCP credentials: {e}")
        raise ValueError(f"Credential validation failed: {e}") from e


@task(
    name="scrape-movies",
    retries=2,
    retry_delay_seconds=30,
    cache_policy=INPUTS + TASK_SOURCE,
    cache_expiration=timedelta(hours=1),
    log_prints=True,
)
def scrape_movies_task() -> list[dict[str, Any]]:
    """
    Task to scrape all movies from GratisTorrent.

    Returns:
        List of movie dictionaries
    """
    logger.info("Starting movie scraping task")
    movies = scrape_all_movies()
    logger.info(f"Scraped {len(movies)} movies")

    return movies


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    items = []
    with open(path, "r") as f:
        for line in f:
            items.append(json.loads(line))
    return items


@task(name="load-to-bigquery", retries=3, retry_delay_seconds=60, log_prints=True)
def load_to_bigquery_task(movies_path: Path) -> int:
    """
    Task to load movies to BigQuery.

    Args:
        movies: List of movie dictionaries

    Returns:
        Number of rows affected in BigQuery
    """
    logger.info("Starting BigQuery load task")
    logger.info(f"Loading movies from {movies_path}...")
    movies = load_jsonl(movies_path)
    if not movies:
        logger.warning("Could not find any movies to load...")
        raise ValueError(f"No movies found in {movies_path}.")
    logger.success(f"{len(movies)} movies loaded from {movies_path}.")
    rows_affected = load_movies_to_bigquery(movies)
    logger.info(f"Loaded {rows_affected} new movies to BigQuery")
    return rows_affected


@flow(name="gratis-torrent-scraper", log_prints=True)
def gratis_torrent_flow() -> dict[str, Any]:
    """
    Main Prefect flow for scraping GratisTorrent and loading to BigQuery.

    This flow orchestrates the scraping and loading pipeline without
    performing any data processing itself.

    Returns:
        Dictionary with pipeline statistics
    """
    logger.info("Starting GratisTorrent scraper flow")

    # Validate credentials before running scraper
    validate_credentials_task()

    # Scrape movies
    movies = scrape_movies_task()

    # Save to disk (jsonl)
    with open(Config.MOVIES_JSON_PATH, "w") as f:
        for movie in movies:
            f.write(json.dumps(movie) + "\n")
    logger.info(f"Saved scraped movies to {Config.MOVIES_JSON_PATH}")

    # Load to BigQuery
    rows_affected = load_to_bigquery_task(Config.MOVIES_JSON_PATH)

    result = {
        "movies_scraped": len(movies),
        "rows_loaded": rows_affected,
    }

    logger.success(f"Flow completed successfully: {result}")
    return result


if __name__ == "__main__":
    gratis_torrent_flow()
