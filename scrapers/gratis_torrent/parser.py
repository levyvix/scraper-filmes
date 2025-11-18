"""Parser functions for extracting movie data from HTML."""

import re

from bs4 import BeautifulSoup
from loguru import logger
from pydantic import ValidationError

from scrapers.gratis_torrent.models import Movie
from scrapers.utils.parse_utils import parse_int, parse_rating, parse_year


def extract_poster_url(soup: BeautifulSoup) -> str | None:
    """
    Extract the poster URL from the movie page.

    Args:
        soup: BeautifulSoup object of the page

    Returns:
        Poster URL string or None if not found
    """
    poster_element = soup.select_one(
        "body > div:nth-child(3) > div > div.col-12.col-sm-8.col-lg-9.my-1 > img"
    )
    if poster_element and "src" in poster_element.attrs:
        return str(poster_element["src"])
    return None


def extract_regex_field(pattern: str, text: str, group: int = 1) -> str | None:
    """
    Extract a single field using regex.

    Args:
        pattern: Regular expression pattern
        text: Text to search in
        group: Regex group number to extract

    Returns:
        Matched string or None if no match found
    """
    match = re.search(pattern, text)
    if not match:
        return None
    return match.group(group).strip()


def extract_sinopse(soup: BeautifulSoup) -> str | None:
    """
    Extract movie synopsis from the page.

    Args:
        soup: BeautifulSoup object of the page

    Returns:
        Synopsis text or None if not found
    """
    sinopse_element = soup.select_one("#sinopse > p")
    if not sinopse_element:
        return None

    sinopse_text: str = sinopse_element.text

    # Remove "Descrição:" prefix if present
    if "Descrição" in sinopse_text:
        sinopse_text = sinopse_text.split("Descrição")[-1]

    # Remove any remaining ":" prefix
    if ":" in sinopse_text:
        sinopse_text = sinopse_text.split(":", 1)[-1]

    return sinopse_text.strip()


def extract_movie_fields(info_text: str) -> dict[str, str | None]:
    """
    Extract all movie fields from info text using regex patterns.

    Args:
        info_text: Raw text containing movie information

    Returns:
        Dictionary of extracted field values
    """
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

    extracted: dict[str, str | None] = {}
    for field_name, pattern in patterns.items():
        extracted[field_name] = extract_regex_field(pattern, info_text)

    return extracted


def clean_genre(genre: str | None) -> str | None:
    """
    Clean up genre field by replacing slashes with commas.

    Args:
        genre: Raw genre string

    Returns:
        Cleaned genre string or None
    """
    if not genre:
        return None
    return genre.replace(" / ", ", ")


def create_movie_object(
    extracted: dict[str, str | None],
    info_text: str,
    sinopse: str | None,
    url: str,
    poster_url: str | None,
) -> Movie | None:
    """
    Create and validate Movie object from extracted data.

    Args:
        extracted: Dictionary of extracted field values
        info_text: Raw info text (used to check for "Português")
        sinopse: Synopsis text
        url: Movie page URL
        poster_url: URL of the movie poster

    Returns:
        Validated Movie object or None if validation fails
    """
    try:
        movie = Movie(
            titulo_dublado=extracted["titulo_dublado"],
            titulo_original=extracted["titulo_original"],
            imdb=parse_rating(extracted["imdb"]),
            ano=parse_year(extracted["ano"]),
            genero=clean_genre(extracted["genero"]),
            tamanho=extracted["tamanho"],
            duracao_minutos=parse_int(extracted["duracao_minutos"]),
            duracao=None,
            qualidade_video=parse_rating(extracted["qualidade_video"]),
            qualidade=extracted["qualidade"],
            dublado="Português" in info_text,
            sinopse=sinopse,
            link=url,
            poster_url=poster_url,
        )
        return movie
    except ValidationError as e:
        logger.error(f"Validation failed for {url}: {e}")
        return None


def parse_movie_page(soup: BeautifulSoup, url: str) -> Movie | None:
    """
    Parse a movie page and extract all information.

    Args:
        soup: BeautifulSoup object of the movie page
        url: URL of the movie page

    Returns:
        Movie object or None if parsing fails
    """
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

    # Extract poster URL
    poster_url = extract_poster_url(soup)

    # Create and return movie object
    return create_movie_object(extracted, info_text, sinopse, url, poster_url)
