"""Main scraper orchestration module."""

from typing import Any

from bs4 import BeautifulSoup
from diskcache import Cache
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from scrapers.gratis_torrent.config import Config
from scrapers.gratis_torrent.http_client import collect_movie_links, fetch_page
from scrapers.gratis_torrent.models import Movie
from scrapers.gratis_torrent.parser import parse_movie_page
from scrapers.utils.constants import (
    DEFAULT_MIN_FIELDS_FILLED_RATIO,
    SCRAPER_RETRY_ATTEMPTS,
    SCRAPER_RETRY_MULTIPLIER,
    SCRAPER_RETRY_WAIT_MAX_SECONDS,
    SCRAPER_RETRY_WAIT_MIN_SECONDS,
)
from scrapers.utils.data_quality import DataQualityChecker
from scrapers.utils.exceptions import FetchException, ScraperException

cache = Cache("movie_cache")


def scrape_movie_links() -> list[str]:
    """
    Scrape movie links from the main page.

    Returns:
        List of movie URLs
    """
    try:
        soup: BeautifulSoup = fetch_page(Config.BASE_URL)
        links = collect_movie_links(soup)
        logger.info(f"Found {len(links)} unique movie links. Scraping details...")
        return links
    except FetchException as e:
        logger.error(f"Cannot access {Config.BASE_URL}: {e}")
        return []


@retry(
    stop=stop_after_attempt(SCRAPER_RETRY_ATTEMPTS),
    wait=wait_exponential(
        multiplier=SCRAPER_RETRY_MULTIPLIER,
        min=SCRAPER_RETRY_WAIT_MIN_SECONDS,
        max=SCRAPER_RETRY_WAIT_MAX_SECONDS,
    ),
    reraise=True,
)
def scrape_movie_details(url: str) -> Movie | None:
    """
    Scrape details for a single movie with retry logic.

    Args:
        url: URL of the movie page

    Returns:
        Movie object or None if parsing fails

    Raises:
        ScraperException: If critical error occurs after retries
    """
    try:
        soup = fetch_page(url)
        movie = parse_movie_page(soup, url)

        if not movie:
            logger.warning(f"No movie data extracted from {url}")
            return None

        return movie

    except FetchException as e:
        logger.error(f"Error fetching {url}: {e}", exc_info=True)
        raise ScraperException(f"Failed to fetch {url}") from e
    except Exception as e:
        logger.error(f"Error scraping {url}: {e}", exc_info=True)
        raise ScraperException(f"Failed to scrape {url}") from e


# @cache.memoize(expire=3600)
def scrape_all_movies() -> list[dict[str, Any]]:
    """
    Scrape all movies from the main page.

    Returns:
        List of movie dictionaries
    """
    links = scrape_movie_links()

    movies_list = []
    failed_links = []
    quality_checker = DataQualityChecker(
        min_fields_filled=DEFAULT_MIN_FIELDS_FILLED_RATIO
    )

    for index, link in enumerate(links, start=1):
        logger.info(f"Processing movie {index}/{len(links)}: {link}")

        try:
            movie = scrape_movie_details(link)
            if not movie:
                logger.warning(f"Failed to extract info from {link}")
                failed_links.append(link)
                continue

            # Validate movie quality before adding to list
            if quality_checker.check_movie(movie):
                movies_list.append(movie.model_dump())
            else:
                logger.warning(f"Movie {link} failed quality checks")
                failed_links.append(link)

        except ScraperException as e:
            logger.error(f"Failed to scrape {link} after retries: {e}")
            failed_links.append(link)
            continue

    logger.info(
        f"Successfully scraped {len(movies_list)} movies. Failed: {len(failed_links)} out of {len(links)}"
    )

    if failed_links:
        logger.warning(f"Failed links: {failed_links[:5]}...")  # Show first 5

    # Log quality report
    if movies_list:
        movies_objects = [Movie(**m) for m in movies_list]
        report = quality_checker.check_batch(movies_objects)
        logger.info(
            f"Quality Report: {report['pass_rate']:.1%} pass rate "
            f"({report['passed_quality']}/{report['total_movies']} movies)"
        )

    return movies_list
