"""Main scraper orchestration module."""

from loguru import logger

from scrapers.gratis_torrent.config import Config
from scrapers.gratis_torrent.http_client import collect_movie_links, fetch_page
from scrapers.gratis_torrent.models import Movie
from scrapers.gratis_torrent.parser import parse_movie_page

from diskcache import Cache


cache = Cache("movie_cache")


def scrape_movie_links() -> list[str]:
    """
    Scrape movie links from the main page.

    Returns:
        List of movie URLs
    """
    soup = fetch_page(Config.BASE_URL)
    if not soup:
        logger.error(f"Cannot access {Config.BASE_URL}. Returning empty list")
        return []

    links = collect_movie_links(soup)
    logger.info(f"Found {len(links)} unique movie links. Scraping details...")
    return links


def scrape_movie_details(url: str) -> Movie | None:
    """
    Scrape details for a single movie.

    Args:
        url: URL of the movie page

    Returns:
        Movie object or None if scraping fails
    """
    soup = fetch_page(url)
    if not soup:
        logger.warning(f"Skipping {url} - could not fetch page")
        return None

    return parse_movie_page(soup, url)


# @cache.memoize(expire=3600)
def scrape_all_movies() -> list[dict]:
    """
    Scrape all movies from the main page.

    Returns:
        List of movie dictionaries
    """
    links = scrape_movie_links()

    movies_list = []
    for index, link in enumerate(links, start=1):
        logger.info(f"Processing movie {index}/{len(links)}: {link}")

        movie = scrape_movie_details(link)
        if not movie:
            logger.warning(f"Failed to extract info from {link}")
            continue

        movies_list.append(movie.model_dump())

    logger.info(f"Successfully scraped {len(movies_list)} movies")
    return movies_list
