"""Prefect flow for GratisTorrent scraper pipeline."""

from prefect import flow, task
from loguru import logger

from src.scrapers.gratis_torrent.bigquery_client import load_movies_to_bigquery
from src.scrapers.gratis_torrent.scraper import scrape_all_movies


@task(name="scrape-movies", retries=2, retry_delay_seconds=30)
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


@task(name="load-to-bigquery", retries=3, retry_delay_seconds=60)
def load_to_bigquery_task(movies: list[dict]) -> int:
    """
    Task to load movies to BigQuery.

    Args:
        movies: List of movie dictionaries

    Returns:
        Number of rows affected in BigQuery
    """
    logger.info("Starting BigQuery load task")
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

    # Load to BigQuery
    rows_affected = load_to_bigquery_task(movies)

    result = {
        "movies_scraped": len(movies),
        "rows_loaded": rows_affected,
    }

    logger.info(f"Flow completed successfully: {result}")
    return result


if __name__ == "__main__":
    gratis_torrent_flow()
