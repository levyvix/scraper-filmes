import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scrapers.gratis_torrent.scraper import scrape_all_movies
from loguru import logger

if __name__ == "__main__":
    logger.remove()
    logger.add(sys.stderr, level="INFO")

    logger.info("Starting test of gratis_torrent scraper...")
    movies = scrape_all_movies()

    if movies:
        logger.info(f"Successfully scraped {len(movies)} movies.")
        for i, movie in enumerate(movies[:5]):  # Print first 5 movies for inspection
            logger.info(f"Movie {i + 1}:")
            for key, value in movie.items():
                logger.info(f"  {key}: {value}")
            logger.info("-" * 20)
    else:
        logger.error("No movies were scraped.")
