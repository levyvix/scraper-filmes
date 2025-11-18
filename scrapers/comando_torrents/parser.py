from scrapling.parser import Adaptor
from scrapers.utils.parse_utils import parse_rating, parse_year
from scrapers.utils.models import Movie
from pydantic import ValidationError
from scrapers.comando_torrents.scraper import fetch_page


def extract_text_or_none(page: Adaptor, selector: str) -> str | None:
    """Extract text from CSS selector, return None if empty or missing."""
    result = page.css_first(selector)
    if not result:
        return None

    text = str(result).strip()
    return text if text else None


def safe_list_get(items: list, index: int, default: str = "") -> str:
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
        print(f"Error: Failed to fetch page from {link}")
        print(f"Details: {error}")
        return None

    info_texts = page.css("div.entry-content.cf > p:nth-child(3)::text")
    if not info_texts:
        print(f"Error: No movie information found at {link}")
        print("Reason: The page structure may have changed or content is missing")
        return None

    if len(info_texts) < 12:
        print(f"Error: Incomplete movie data at {link}")
        print(f"Details: Expected 12 fields, found {len(info_texts)}")
        return None

    imdb_text = extract_text_or_none(page, "div.entry-content.cf > p:nth-child(3) > a:nth-child(7)::text")
    imdb_rating = parse_rating(imdb_text)

    year_text = extract_text_or_none(page, "div.entry-content.cf > p:nth-child(3) > a:nth-child(10)::text")
    # TODO: consertar busca por ano do filme
    year = parse_year(year_text)
    if not year:
        year_fallback = safe_list_get(info_texts, 3)
        year = parse_year(year_fallback)

    sinopse_list = page.css("div.entry-content.cf > p:nth-child(4)::text")
    sinopse = str(sinopse_list[0]).strip() if sinopse_list else None

    audio_text = safe_list_get(info_texts, 7, "").strip()
    is_dubbed = "Português" in audio_text

    poster_url_selector = "div.entry-content.cf img::attr(src)"
    poster_url_result = page.css_first(poster_url_selector)
    poster_url = str(poster_url_result).strip() if poster_url_result else None

    try:
        movie = Movie(
            titulo_dublado=safe_list_get(info_texts, 0).replace(":", "").strip(),
            titulo_original=safe_list_get(info_texts, 1).replace(":", "").strip(),
            imdb=str(imdb_rating) if imdb_rating else None,
            ano=year,
            genero=safe_list_get(info_texts, 4).replace(":", "").strip(),
            qualidade=safe_list_get(info_texts, 6).strip(),
            dublado=is_dubbed,
            tamanho=safe_list_get(info_texts, 9).strip(),
            duracao=safe_list_get(info_texts, 10).strip(),
            qualidade_video=parse_rating(safe_list_get(info_texts, 11)),
            sinopse=sinopse.replace(":", "").strip() if sinopse else None,
            link=link,
            poster_url=poster_url,
        )
        return movie
    except ValidationError as error:
        print(f"Error: Invalid movie data at {link}")
        print(f"Details: {error}")
        return None
