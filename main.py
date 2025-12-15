"""
Script to run the GratisTorrent scraper standalone (no Prefect server required).
"""

from loguru import logger

from scrapers.gratis_torrent.bigquery_client import load_movies_to_bigquery
from scrapers.gratis_torrent.scraper import scrape_all_movies


def main() -> dict:
    """
    Run the scraper pipeline standalone.

    Returns:
        Dictionary with pipeline statistics
    """
    logger.info("Starting GratisTorrent scraper (standalone mode)")

    # Scrape movies
    logger.info("Scraping movies...")
    movies = scrape_all_movies()
    logger.info(f"Scraped {len(movies)} movies")

    # Load to BigQuery
    logger.info("Loading to BigQuery...")
    rows_affected = load_movies_to_bigquery(movies)
    logger.info(f"Loaded {rows_affected} new movies to BigQuery")

    result = {
        "movies_scraped": len(movies),
        "rows_loaded": rows_affected,
    }

    logger.info(f"Pipeline completed successfully: {result}")
    return result


if __name__ == "__main__":
    main()
