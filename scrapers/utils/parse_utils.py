def parse_rating(rating_text: str | None) -> float | None:
    """Convert rating text to float, return None if invalid."""
    if not rating_text:
        return None

    try:
        return float(rating_text.replace(",", ".").strip())
    except ValueError:
        return None


def parse_year(year_text: str | None) -> int | None:
    """Convert year text to integer, return None if invalid."""
    if not year_text:
        return None

    clean_year = year_text.strip()
    if not clean_year.isdigit():
        return None

    return int(clean_year)


def parse_int(text: str | None) -> int | None:
    """Convert text to integer, return None if invalid."""
    if not text:
        return None

    try:
        return int(text.strip())
    except (ValueError, TypeError):
        return None
