"""Parser functions for extracting movie data from HTML."""

import re

from bs4 import BeautifulSoup
from loguru import logger
from pydantic import ValidationError

from scrapers.gratis_torrent.models import Movie


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


def safe_convert_float(value: str | None) -> float | None:
    """
    Convert string to float, return None if conversion fails.

    Args:
        value: String value to convert

    Returns:
        Float value or None if conversion fails
    """
    if not value:
        return None

    try:
        return float(value)
    except (ValueError, TypeError):
        logger.warning(f"Cannot convert '{value}' to float. Skipping this field.")
        return None


def safe_convert_int(value: str | None) -> int | None:
    """
    Convert string to integer, return None if conversion fails.

    Args:
        value: String value to convert

    Returns:
        Integer value or None if conversion fails
    """
    if not value:
        return None

    try:
        return int(value)
    except (ValueError, TypeError):
        logger.warning(f"Cannot convert '{value}' to integer. Skipping this field.")
        return None


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

    sinopse_text = sinopse_element.text

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

    extracted = {}
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


def create_movie_object(extracted: dict, info_text: str, sinopse: str | None, url: str) -> Movie | None:
    """
    Create and validate Movie object from extracted data.

    Args:
        extracted: Dictionary of extracted field values
        info_text: Raw info text (used to check for "Português")
        sinopse: Synopsis text
        url: Movie page URL

    Returns:
        Validated Movie object or None if validation fails
    """
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

    # Create and return movie object
    return create_movie_object(extracted, info_text, sinopse, url)
