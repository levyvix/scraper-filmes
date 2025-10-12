"""Tests for parser module."""

from bs4 import BeautifulSoup

from src.scrapers.gratis_torrent.parser import (
    clean_genre,
    create_movie_object,
    extract_movie_fields,
    extract_regex_field,
    extract_sinopse,
    parse_movie_page,
    safe_convert_float,
    safe_convert_int,
)


class TestExtractRegexField:
    """Tests for extract_regex_field function."""

    def test_extract_simple_pattern(self):
        """Test extracting a simple pattern."""
        text = "Título: The Matrix"
        pattern = r"Título:\s*(.+)"
        result = extract_regex_field(pattern, text)
        assert result == "The Matrix"

    def test_extract_no_match(self):
        """Test when pattern doesn't match."""
        text = "Something else"
        pattern = r"Título:\s*(.+)"
        result = extract_regex_field(pattern, text)
        assert result is None

    def test_extract_with_group(self):
        """Test extracting specific group."""
        text = "Year: 1999, Director: Wachowski"
        pattern = r"Year:\s*(\d+),\s*Director:\s*(.+)"
        result = extract_regex_field(pattern, text, group=2)
        assert result == "Wachowski"


class TestSafeConvertFloat:
    """Tests for safe_convert_float function."""

    def test_convert_valid_float(self):
        """Test converting valid float string."""
        assert safe_convert_float("8.5") == 8.5

    def test_convert_valid_integer_string(self):
        """Test converting integer string to float."""
        assert safe_convert_float("8") == 8.0

    def test_convert_none(self):
        """Test converting None."""
        assert safe_convert_float(None) is None

    def test_convert_empty_string(self):
        """Test converting empty string."""
        assert safe_convert_float("") is None

    def test_convert_invalid_string(self):
        """Test converting invalid string."""
        assert safe_convert_float("not a number") is None


class TestSafeConvertInt:
    """Tests for safe_convert_int function."""

    def test_convert_valid_integer(self):
        """Test converting valid integer string."""
        assert safe_convert_int("120") == 120

    def test_convert_none(self):
        """Test converting None."""
        assert safe_convert_int(None) is None

    def test_convert_empty_string(self):
        """Test converting empty string."""
        assert safe_convert_int("") is None

    def test_convert_invalid_string(self):
        """Test converting invalid string."""
        assert safe_convert_int("not a number") is None

    def test_convert_float_string(self):
        """Test converting float string."""
        assert safe_convert_int("8.5") is None


class TestExtractSinopse:
    """Tests for extract_sinopse function."""

    def test_extract_sinopse_simple(self):
        """Test extracting simple synopsis."""
        html = '<div id="sinopse"><p>This is the synopsis</p></div>'
        soup = BeautifulSoup(html, "html.parser")
        result = extract_sinopse(soup)
        assert result == "This is the synopsis"

    def test_extract_sinopse_with_prefix(self):
        """Test extracting synopsis with 'Descrição:' prefix."""
        html = '<div id="sinopse"><p>Descrição: This is the synopsis</p></div>'
        soup = BeautifulSoup(html, "html.parser")
        result = extract_sinopse(soup)
        assert result == "This is the synopsis"

    def test_extract_sinopse_with_colon(self):
        """Test extracting synopsis with colon prefix."""
        html = '<div id="sinopse"><p>: This is the synopsis</p></div>'
        soup = BeautifulSoup(html, "html.parser")
        result = extract_sinopse(soup)
        assert result == "This is the synopsis"

    def test_extract_sinopse_not_found(self):
        """Test when synopsis element is not found."""
        html = "<div><p>No synopsis here</p></div>"
        soup = BeautifulSoup(html, "html.parser")
        result = extract_sinopse(soup)
        assert result is None


class TestExtractMovieFields:
    """Tests for extract_movie_fields function."""

    def test_extract_all_fields(self):
        """Test extracting all movie fields."""
        info_text = """
        Baixar The Matrix Torrent
        Título Original: The Matrix
        Imdb: 8.7 /10
        Lançamento: 1999
        Gêneros: Action / Sci-Fi Idioma: English
        Tamanho: 2.5 GB
        Duração: 136 Minutos
        Vídeo: 10 | Áudio: 10
        Qualidade: 1080p BluRay
        """

        result = extract_movie_fields(info_text)

        assert result["titulo_dublado"] == "The Matrix"
        assert result["titulo_original"] == "The Matrix"
        assert result["imdb"] == "8.7"
        assert result["ano"] == "1999"
        assert result["genero"] == "Action / Sci-Fi"
        assert result["tamanho"] == "2.5"
        assert result["duracao_minutos"] == "136"
        assert result["qualidade_video"] == "10"
        assert result["qualidade"] == "1080p BluRay"

    def test_extract_partial_fields(self):
        """Test extracting when some fields are missing."""
        info_text = """
        Baixar The Matrix Torrent
        Lançamento: 1999
        """

        result = extract_movie_fields(info_text)

        assert result["titulo_dublado"] == "The Matrix"
        assert result["ano"] == "1999"
        assert result["imdb"] is None
        assert result["genero"] is None


class TestCleanGenre:
    """Tests for clean_genre function."""

    def test_clean_genre_with_slashes(self):
        """Test cleaning genre with slashes."""
        result = clean_genre("Action / Sci-Fi / Adventure")
        assert result == "Action, Sci-Fi, Adventure"

    def test_clean_genre_no_slashes(self):
        """Test cleaning genre without slashes."""
        result = clean_genre("Action")
        assert result == "Action"

    def test_clean_genre_none(self):
        """Test cleaning None genre."""
        result = clean_genre(None)
        assert result is None


class TestCreateMovieObject:
    """Tests for create_movie_object function."""

    def test_create_valid_movie(self):
        """Test creating valid movie object."""
        extracted = {
            "titulo_dublado": "The Matrix",
            "titulo_original": "The Matrix",
            "imdb": "8.7",
            "ano": "1999",
            "genero": "Action / Sci-Fi",
            "tamanho": "2.5",
            "duracao_minutos": "136",
            "qualidade_video": "10",
            "qualidade": "1080p BluRay",
        }
        info_text = "Idioma: Português"
        sinopse = "A computer hacker learns about the true nature of reality."
        url = "https://example.com/matrix"

        movie = create_movie_object(extracted, info_text, sinopse, url)

        assert movie is not None
        assert movie.titulo_dublado == "The Matrix"
        assert movie.imdb == 8.7
        assert movie.ano == 1999
        assert movie.dublado is True
        assert movie.sinopse == sinopse
        assert movie.link == url

    def test_create_movie_not_dubbed(self):
        """Test creating movie that's not dubbed."""
        extracted = {
            "titulo_dublado": "The Matrix",
            "titulo_original": "The Matrix",
            "imdb": "8.7",
            "ano": "1999",
            "genero": "Action",
            "tamanho": "2.5",
            "duracao_minutos": "136",
            "qualidade_video": "10",
            "qualidade": "1080p",
        }
        info_text = "Idioma: English"
        url = "https://example.com/matrix"

        movie = create_movie_object(extracted, info_text, None, url)

        assert movie is not None
        assert movie.dublado is False

    def test_create_movie_invalid_data(self):
        """Test creating movie with invalid data."""
        extracted = {
            "titulo_dublado": "Movie",
            "titulo_original": "Movie",
            "imdb": "15.0",  # Invalid - over 10
            "ano": "1800",  # Invalid - before 1888
            "genero": None,
            "tamanho": None,
            "duracao_minutos": "-5",  # Invalid - negative
            "qualidade_video": None,
            "qualidade": None,
        }
        info_text = "Idioma: English"
        url = "https://example.com/movie"

        movie = create_movie_object(extracted, info_text, None, url)

        assert movie is None


class TestParseMoviePage:
    """Tests for parse_movie_page function."""

    def test_parse_complete_page(self):
        """Test parsing a complete movie page."""
        html = """
        <html>
            <div id="informacoes">
                <p>
                    Baixar The Matrix Torrent
                    Título Original: The Matrix
                    Imdb: 8.7 /10
                    Lançamento: 1999
                    Gêneros: Action / Sci-Fi Idioma: Português
                    Tamanho: 2.5 GB
                    Duração: 136 Minutos
                    Vídeo: 10 | Áudio: 10
                    Qualidade: 1080p BluRay
                </p>
            </div>
            <div id="sinopse">
                <p>A computer hacker learns about reality.</p>
            </div>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        url = "https://example.com/matrix"

        movie = parse_movie_page(soup, url)

        assert movie is not None
        assert movie.titulo_dublado == "The Matrix"
        assert movie.ano == 1999
        assert movie.dublado is True

    def test_parse_page_no_info(self):
        """Test parsing page without info section."""
        html = "<html><body>No info here</body></html>"
        soup = BeautifulSoup(html, "html.parser")
        url = "https://example.com/movie"

        movie = parse_movie_page(soup, url)

        assert movie is None
