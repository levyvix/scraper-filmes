from scrapers.gratis_torrent.parser import clean_genre, extract_regex_field


def test_clean_genre():
    """Test the clean_genre function."""
    assert clean_genre("Action / Sci-Fi") == "Action, Sci-Fi"
    assert clean_genre("Drama | Comedy") == "Drama, Comedy"
    assert clean_genre("Horror") == "Horror"
    assert clean_genre(None) is None


def test_extract_regex_field():
    """Test the extract_regex_field function."""
    text = "Título: The Matrix"
    pattern = r"Título:\s*(.+)"
    assert extract_regex_field(pattern, text) == "The Matrix"

    text_no_match = "Ano: 1999"
    assert extract_regex_field(pattern, text_no_match) is None
