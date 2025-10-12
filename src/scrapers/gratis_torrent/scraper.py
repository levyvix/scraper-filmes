"""Main scraper orchestration module."""

from loguru import logger

from .config import Config
from .http_client import collect_movie_links, fetch_page
from .models import Movie
from .parser import parse_movie_page


def scrape_movie_links() -> list[str]:
    """
    Scrape movie links from the main page.

    Returns:
        List of movie URLs
    """
    soup = fetch_page(Config.BASE_URL)
    if not soup:
        logger.error(f"Cannot access {Config.BASE_URL}")
        return []

    links = collect_movie_links(soup)
    logger.info(f"Found {len(links)} unique movie links")
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
