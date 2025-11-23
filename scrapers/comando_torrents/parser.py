from scrapling.parser import Adaptor
from scrapers.utils.parse_utils import parse_rating, parse_year
from scrapers.utils.models import Movie
from pydantic import ValidationError
from loguru import logger
from scrapers.comando_torrents.scraper import fetch_page


def extract_text_or_none(page: Adaptor, selector: str) -> str | None:
    """Extract text from CSS selector, return None if empty or missing."""
    result = page.css_first(selector)
    if not result:
        return None

    text = str(result).strip()
    return text if text else None


def safe_list_get(items: list[str], index: int, default: str = "") -> str:
    """Safely get item from list by index, return default if out of range."""
    if index < 0 or index >= len(items):
        return default
    return items[index]


def parse_detail(link: str) -> Movie | None:
    """Parse movie details from a given link."""
    try:
        page = fetch_page(link)
        if not page:
            return None
    except Exception as error:
        logger.error(f"Failed to fetch page from {link}: {error}")
        return None

    info_texts = page.css("div.entry-content.cf > p:nth-child(3)::text")
    if not info_texts:
        logger.error(
            f"No movie information found at {link}. The page structure may have changed or content is missing."
        )
        return None

    info_texts_str = [str(t) for t in info_texts]

    if len(info_texts_str) < 12:
        logger.warning(
            f"Incomplete movie data at {link}. Expected 12 fields, found {len(info_texts_str)}"
        )
        return None

    imdb_text = extract_text_or_none(
        page, "div.entry-content.cf > p:nth-child(3) > a:nth-child(7)::text"
    )
    imdb_rating = parse_rating(imdb_text)

    year_text = extract_text_or_none(
        page, "div.entry-content.cf > p:nth-child(3) > a:nth-child(10)::text"
    )
    # Extract year with multiple fallback strategies
    # First try: Direct CSS selector (most reliable)
    year = parse_year(year_text)

    # Second try: Fallback to structured data at index 3 if CSS selector fails
    if not year:
        year_fallback = safe_list_get(info_texts_str, 3)
        year = parse_year(year_fallback)

    # Third try: Search for any 4-digit number that looks like a year (1888-2100)
    if not year and info_texts_str:
        for text in info_texts_str:
            potential_year = parse_year(text)
            if potential_year and 1888 <= potential_year <= 2100:
                year = potential_year
                break

    sinopse_list = page.css("div.entry-content.cf > p:nth-child(4)::text")
    sinopse = str(sinopse_list[0]).strip() if sinopse_list else None

    audio_text = safe_list_get(info_texts_str, 7, "").strip()
    is_dubbed = "Português" in audio_text

    poster_url_selector = "div.entry-content.cf img::attr(src)"
    poster_url_result = page.css_first(poster_url_selector)
    poster_url = str(poster_url_result).strip() if poster_url_result else None

    try:
        movie = Movie(
            titulo_dublado=safe_list_get(info_texts_str, 0).replace(":", "").strip(),
            titulo_original=safe_list_get(info_texts_str, 1).replace(":", "").strip(),
            imdb=imdb_rating,
            ano=year,
            genero=safe_list_get(info_texts_str, 4).replace(":", "").strip(),
            qualidade=safe_list_get(info_texts_str, 6).strip(),
            dublado=is_dubbed,
            tamanho=safe_list_get(info_texts_str, 9).strip(),
            duracao=safe_list_get(info_texts_str, 10).strip(),
            qualidade_video=parse_rating(safe_list_get(info_texts_str, 11)),
            sinopse=sinopse.replace(":", "").strip() if sinopse else None,
            link=link,
            poster_url=poster_url,
        )
        return movie
    except ValidationError as error:
        logger.error(f"Invalid movie data at {link}: {error}")
        return None
