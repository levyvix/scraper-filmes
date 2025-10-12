import json
from pathlib import Path
from scrapling.fetchers import StealthySession
from scrapling.parser import Adaptor
from pydantic import BaseModel, Field, ValidationError
from diskcache import Cache

cache = Cache("./comando_cache")


class Movie(BaseModel):
    """Movie data model with validation."""

    titulo_dublado: str | None = None
    titulo_original: str | None = None
    imdb: str | None = None
    ano: int | None = Field(None, ge=1888)
    genero: str | None = None
    tamanho: str | None = None
    duracao: str | None = None
    qualidade_video: float | None = Field(None, ge=0, description="Video quality score (0-10)")
    qualidade: str | None = Field(None, description="Quality description (e.g., '1080p', '720p BluRay')")
    dublado: bool | None = None
    sinopse: str | None = None
    link: str | None = None


@cache.memoize()
def fetch_page_html(url: str) -> tuple[str, str] | None:
    """Fetch HTML content from a web page with stealth settings. Returns (html, url) tuple."""
    try:
        with StealthySession(headless=True, solve_cloudflare=True) as session:
            page = session.fetch(url)
            return (page.html_content, url)
    except Exception as error:
        print(f"Error: Failed to fetch page from {url}")
        print(f"Details: {error}")
        return None


def fetch_page(url: str):
    """Fetch a web page and return an Adaptor object for parsing."""
    result = fetch_page_html(url)
    if result is None:
        return None
    html, original_url = result
    # Create an Adaptor object from the cached HTML
    return Adaptor(html, url=original_url)


def extract_text_or_none(page, selector: str) -> str | None:
    """Extract text from CSS selector, return None if empty or missing."""
    result = page.css_first(selector)
    if not result:
        return None

    text = str(result).strip()
    return text if text else None


def parse_year(year_text: str | None) -> int | None:
    """Convert year text to integer, return None if invalid."""
    if not year_text:
        return None

    clean_year = year_text.strip()
    if not clean_year.isdigit():
        return None

    return int(clean_year)


def parse_rating(rating_text: str | None) -> float | None:
    """Convert rating text to float, return None if invalid."""
    if not rating_text:
        return None

    try:
        return float(rating_text.replace(",", ".").strip())
    except ValueError:
        return None


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
    year = parse_year(year_text)
    if not year:
        year_fallback = safe_list_get(info_texts, 3)
        year = parse_year(year_fallback)

    sinopse_list = page.css("div.entry-content.cf > p:nth-child(4)::text")
    sinopse = str(sinopse_list[0]).strip() if sinopse_list else None

    audio_text = safe_list_get(info_texts, 7, "").strip()
    is_dubbed = "Português" in audio_text

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
        )
        return movie
    except ValidationError as error:
        print(f"Error: Invalid movie data at {link}")
        print(f"Details: {error}")
        return None


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


def main():
    """Main function to scrape movies and save to JSON."""
    base_url = "https://comando.la/category/filmes/"

    print(f"Fetching movie links from {base_url}")
    links = get_movie_links(base_url)

    if not links:
        print("Error: No movie links found. Please check the website or your connection.")
        return

    print(f"Found {len(links)} movie links. Starting to scrape...")

    list_movies: list[Movie] = []
    for index, link in enumerate(links, start=1):
        print(f"Processing movie {index}/{len(links)}: {link}")

        movie = parse_detail(str(link))
        if movie:
            list_movies.append(movie)

    if not list_movies:
        print("Error: No movies were successfully scraped.")
        return

    json_path = Path(__file__).parent / "movies.json"
    json_data = json.dumps([movie.model_dump(mode="json") for movie in list_movies], indent=2, ensure_ascii=False)
    json_path.write_text(json_data, encoding="utf-8")

    print(f"Success: Saved {len(list_movies)} movies to {json_path}")


if __name__ == "__main__":
    main()
