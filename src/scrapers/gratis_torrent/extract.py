from typing import Optional
import requests
from bs4 import BeautifulSoup
import json
import re
from pydantic import BaseModel, Field, ValidationError
from rich import print
from loguru import logger
import sys

logger.remove()
logger.add(sys.stderr, level="WARNING")


class Movie(BaseModel):
    titulo_dublado: str | None = None
    titulo_original: str | None = None
    imdb: float | None = Field(None, ge=0, le=10)
    ano: int | None = Field(None, ge=1888)
    genero: str | None = None
    tamanho: str | None = None
    duracao_minutos: int | None = Field(None, ge=1)
    qualidade_video: float | None = Field(None, ge=0, description="Video quality score (0-10)")
    qualidade: str | None = Field(None, description="Quality description (e.g., '1080p', '720p BluRay')")
    dublado: bool | None = None
    sinopse: str | None = None
    link: str | None = None


def extract_regex_field(pattern: str, text: str, group: int = 1) -> str | None:
    """
    Extract a single field using regex.
    Returns the matched group or None if no match found.
    """
    match = re.search(pattern, text)
    if not match:
        return None
    return match.group(group).strip()


def safe_convert_float(value: str | None) -> float | None:
    """Convert string to float, return None if conversion fails."""
    if not value:
        return None

    try:
        return float(value)
    except (ValueError, TypeError):
        logger.warning(f"Cannot convert '{value}' to float. Skipping this field.")
        return None


def safe_convert_int(value: str | None) -> int | None:
    """Convert string to integer, return None if conversion fails."""
    if not value:
        return None

    try:
        return int(value)
    except (ValueError, TypeError):
        logger.warning(f"Cannot convert '{value}' to integer. Skipping this field.")
        return None


def fetch_page(url: str) -> BeautifulSoup | None:
    """
    Fetch and parse HTML page.
    Returns BeautifulSoup object or None if request fails.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return None


def extract_sinopse(soup: BeautifulSoup) -> str | None:
    """Extract movie synopsis from the page."""
    sinopse_element = soup.select_one("#sinopse > p")
    if not sinopse_element:
        return None

    sinopse_text = sinopse_element.text

    # Remove "Descrição:" prefix if present
    if "Descrição" in sinopse_text:
        sinopse_text = sinopse_text.split("Descrição")[-1]

    # Remove any remaining ":" prefix
    if ":" in sinopse_text:
        sinopse_text = sinopse_text.split(":", 1)[-1]

    return sinopse_text.strip()


def extract_movie_fields(info_text: str) -> dict[str, str | None]:
    """Extract all movie fields from info text using regex patterns."""
    # Define all regex patterns in one place
    patterns = {
        "titulo_dublado": r"Baixar (.+) Torrent",
        "titulo_original": r"Título Original:\s*(.+)\s*",
        "imdb": r"Imdb:\s*(.+)\s*/",
        "ano": r"Lançamento:\s*(\d{4})",
        "genero": r"Gêneros:\s*(.+)\s*Idioma:",
        "tamanho": r"Tamanho:\s*(.+)\s*GB",
        "duracao_minutos": r"Duração:\s*(\d+) Minutos",
        "qualidade_video": r"Vídeo:\s*([0-9]+)\s*\|",
        "qualidade": r"Qualidade:\s*([0-9a-zA-Z |]+)",
    }

    # Extract all fields
    extracted = {}
    for field_name, pattern in patterns.items():
        extracted[field_name] = extract_regex_field(pattern, info_text)

    return extracted


def clean_genre(genre: str | None) -> str | None:
    """Clean up genre field by replacing slashes with commas."""
    if not genre:
        return None
    return genre.replace(" / ", ", ")


def create_movie_object(extracted: dict, info_text: str, sinopse: str | None, url: str) -> Movie | None:
    """Create and validate Movie object from extracted data."""
    try:
        movie = Movie(
            titulo_dublado=extracted["titulo_dublado"],
            titulo_original=extracted["titulo_original"],
            imdb=safe_convert_float(extracted["imdb"]),
            ano=safe_convert_int(extracted["ano"]),
            genero=clean_genre(extracted["genero"]),
            tamanho=extracted["tamanho"],
            duracao_minutos=safe_convert_int(extracted["duracao_minutos"]),
            qualidade_video=safe_convert_float(extracted["qualidade_video"]),
            qualidade=extracted["qualidade"],
            dublado="Português" in info_text,
            sinopse=sinopse,
            link=url,
        )
        return movie
    except ValidationError as e:
        logger.error(f"Validation failed for {url}: {e}")
        return None


def extract_info(url: str) -> Optional[Movie]:
    """
    Extract movie information from a Gratis Torrent page.
    Returns Movie object or None if extraction fails.
    """
    # Fetch the page
    soup = fetch_page(url)
    if not soup:
        logger.warning(f"Skipping {url} - could not fetch page")
        return None

    # Get main info text
    info_element = soup.select_one("#informacoes > p")
    if not info_element:
        logger.warning(f"Skipping {url} - no info section found")
        return None

    # Normalize the info text
    info_text = info_element.text
    info_text = re.sub(r": \n", ": ", info_text)
    logger.debug(info_text)

    # Extract all fields
    extracted = extract_movie_fields(info_text)

    # Extract synopsis
    sinopse = extract_sinopse(soup)

    # Create and return movie object
    return create_movie_object(extracted, info_text, sinopse, url)


def collect_movie_links(soup: BeautifulSoup) -> list[str]:
    """Collect all unique movie links from the page."""
    elements = soup.select("#capas_pequenas > div > a")

    links = []
    for element in elements:
        link = element.get("href")
        if link:
            links.append(link)

    # Remove duplicates while preserving order
    unique_links = list(dict.fromkeys(links))
    return unique_links


def main():
    website = "https://gratistorrent.com/lancamentos/"

    # Fetch the main page
    soup = fetch_page(website)
    if not soup:
        logger.error(f"Cannot access {website}. Exiting.")
        return

    # Collect all movie links
    logger.info("Getting Movies...")
    links = collect_movie_links(soup)
    logger.info(f"Found {len(links)} unique movie links")

    # Extract movie information
    movies_list = []
    for index, link in enumerate(links, start=1):
        logger.info(f"Processing movie {index}/{len(links)}: {link}")

        movie = extract_info(link)
        if not movie:
            logger.warning(f"Failed to extract info from {link}")
            continue

        print(movie)
        movies_list.append(movie.model_dump())

    # Save to JSON file
    logger.info(f"Successfully scraped {len(movies_list)} movies")
    with open("movies_gratis.json", "w", encoding="utf-8") as f:
        json.dump(movies_list, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
