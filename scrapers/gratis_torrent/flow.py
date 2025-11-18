"""Prefect flow for GratisTorrent scraper pipeline."""

import json

from pathlib import Path

from prefect import flow, task
from prefect.cache_policies import INPUTS, TASK_SOURCE
from loguru import logger

from scrapers.gratis_torrent.bigquery_client import load_movies_to_bigquery
from scrapers.gratis_torrent.scraper import scrape_all_movies
from scrapers.gratis_torrent.config import Config
from datetime import timedelta


@task(
    name="scrape-movies",
    retries=2,
    retry_delay_seconds=30,
    log_prints=True,
)
def scrape_movies_task() -> list[dict]:
    """
    Task to scrape all movies from GratisTorrent.

    Returns:
        List of movie dictionaries
    """
    logger.info("Starting movie scraping task")
    movies = scrape_all_movies()
    logger.info(f"Scraped {len(movies)} movies")

    return movies


def load_jsonl(path: Path) -> list[dict]:
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
    movies = load_jsonl(movies_path)
    rows_affected = load_movies_to_bigquery(movies)
    logger.info(f"Loaded {rows_affected} new movies to BigQuery")
    return rows_affected


@flow(name="gratis-torrent-scraper", log_prints=True)
def gratis_torrent_flow() -> dict:
    """
    Main Prefect flow for scraping GratisTorrent and loading to BigQuery.

    This flow orchestrates the scraping and loading pipeline without
    performing any data processing itself.

    Returns:
        Dictionary with pipeline statistics
    """
    logger.info("Starting GratisTorrent scraper flow")

    # Scrape movies
    movies = scrape_movies_task()

    # Save to disk
    # save jsonl
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
