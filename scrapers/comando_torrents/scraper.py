from scrapling.fetchers import StealthySession
from scrapling.parser import Adaptor, Selector
from diskcache import Cache

cache = Cache("./comando_cache")


@cache.memoize()
def fetch_page_html(url: str) -> tuple[str, str] | None:
    """Fetch HTML content from a web page with stealth settings. Returns (html, url) tuple."""
    try:
        with StealthySession(headless=True, solve_cloudflare=True) as session:
            page: Selector = session.fetch(url)
            return (page.html_content, url)
    except Exception as error:
        print(f"Error: Failed to fetch page from {url}")
        print(f"Details: {error}")
        return None


def fetch_page(url: str) -> Adaptor | None:
    """Fetch a web page and return an Adaptor object for parsing."""
    result = fetch_page_html(url)
    if result is None:
        return None
    html, original_url = result
    # Create an Adaptor object from the cached HTML
    return Adaptor(html, url=original_url)


def get_movie_links(url: str) -> list[str]:
    """Fetch movie links from the main category page."""
    try:
        page = fetch_page(url)
        if not page:
            return []
        links = page.css("article > header > h2 > a::attr(href)")
        return [str(link) for link in links]
    except Exception as error:
        print(f"Error: Failed to fetch movie links from {url}")
        print(f"Details: {error}")
        return []
