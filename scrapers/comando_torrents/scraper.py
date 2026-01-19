try:
    from scrapling.fetchers import StealthySession
    from scrapling.parser import Adaptor, Selector
except (ImportError, FileNotFoundError) as e:
    raise ImportError(
        "scrapling and camoufox are required for comando_torrents scraper. Install with: uv add scrapling camoufox"
    ) from e

from diskcache import Cache
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from scrapers.utils.rate_limiter import rate_limit

cache = Cache("./comando_cache")


@rate_limit(calls_per_second=2.0)  # Max 2 requests per second
@cache.memoize()
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    reraise=True,
)
def fetch_page_html(url: str) -> tuple[str, str]:
    """
    Fetch HTML content from a web page with stealth settings.

    Args:
        url: URL to fetch

    Returns:
        Tuple of (html_content, url)

    Raises:
        FetchException: If fetching fails after retries
    """
    from scrapers.utils.exceptions import FetchException

    try:
        with StealthySession(headless=True, solve_cloudflare=True) as session:
            page: Selector = session.fetch(url)
            return (page.html_content, url)
    except Exception as error:
        logger.error(f"Failed to fetch page from {url}: {error}", exc_info=True)
        raise FetchException(f"Failed to fetch {url}") from error


def fetch_page(url: str) -> Adaptor:
    """
    Fetch a web page and return an Adaptor object for parsing.

    Args:
        url: URL to fetch

    Returns:
        Adaptor object for parsing

    Raises:
        FetchException: If fetching fails
    """
    html, original_url = fetch_page_html(url)
    # Create an Adaptor object from the cached HTML
    return Adaptor(html, url=original_url)


def get_movie_links(url: str) -> list[str]:
    """
    Fetch movie links from the main category page.

    Args:
        url: URL of the category page

    Returns:
        List of movie URLs, empty list if fetching fails
    """
    from scrapers.utils.exceptions import FetchException

    try:
        page = fetch_page(url)
        links = page.css("article > header > h2 > a::attr(href)")
        return [str(link) for link in links]
    except FetchException as error:
        logger.error(f"Failed to fetch movie links from {url}: {error}")
        return []
    except Exception as error:
        logger.error(
            f"Unexpected error fetching movie links from {url}: {error}", exc_info=True
        )
        return []
