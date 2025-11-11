"""HTTP client for fetching web pages."""

import requests
from bs4 import BeautifulSoup
from loguru import logger

from src.scrapers.gratis_torrent.config import Config


def fetch_page(url: str, timeout: int = Config.REQUEST_TIMEOUT) -> BeautifulSoup | None:
    """
    Fetch and parse HTML page.

    Args:
        url: URL to fetch
        timeout: Request timeout in seconds

    Returns:
        BeautifulSoup object or None if request fails
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return None


def collect_movie_links(soup: BeautifulSoup) -> list[str]:
    """
    Collect all unique movie links from the page.

    Args:
        soup: BeautifulSoup object of the page

    Returns:
        List of unique movie URLs
    """
    elements = soup.select("#capas_pequenas > div > a")

    links = []
    for element in elements:
        link = element.get("href")
        if link:
            links.append(link)

    # Remove duplicates while preserving order
    return list(set(links))
