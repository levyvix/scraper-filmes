"""Tests for GratisTorrent parser module."""

from bs4 import BeautifulSoup
from scrapers.gratis_torrent.parser import (
    clean_genre,
    extract_regex_field,
    extract_poster_url,
    extract_sinopse,
    extract_movie_fields,
    create_movie_object,
    parse_movie_page,
)


class TestCleanGenre:
    """Test the clean_genre function."""

    def test_clean_genre_slash_separator(self):
        """Test genre cleaning with slash separator."""
        assert clean_genre("Action / Sci-Fi") == "Action, Sci-Fi"

    def test_clean_genre_pipe_separator(self):
        """Test genre cleaning with pipe separator."""
        assert clean_genre("Drama | Comedy") == "Drama, Comedy"

    def test_clean_genre_no_separator(self):
        """Test genre with no separators."""
        assert clean_genre("Horror") == "Horror"

    def test_clean_genre_none(self):
        """Test clean_genre with None input."""
        assert clean_genre(None) is None

    def test_clean_genre_empty_string(self):
        """Test clean_genre with empty string."""
        assert clean_genre("") is None

    def test_clean_genre_multiple_separators(self):
        """Test genre with multiple different separators."""
        result = clean_genre("Action / Drama | Comedy")
        assert result == "Action, Drama, Comedy"

    def test_clean_genre_with_spaces(self):
        """Test genre cleaning preserves non-separator spaces."""
        assert clean_genre("Sci-Fi / Action") == "Sci-Fi, Action"


class TestExtractRegexField:
    """Test the extract_regex_field function."""

    def test_extract_regex_field_simple(self):
        """Test basic regex extraction."""
        text = "Título: The Matrix"
        pattern = r"Título:\s*(.+)"
        assert extract_regex_field(pattern, text) == "The Matrix"

    def test_extract_regex_field_no_match(self):
        """Test extraction when pattern doesn't match."""
        text = "Ano: 1999"
        pattern = r"Título:\s*(.+)"
        assert extract_regex_field(pattern, text) is None

    def test_extract_regex_field_with_numbers(self):
        """Test extraction of numeric content."""
        text = "Imdb: 8.7 / 10"
        pattern = r"Imdb:\s*([0-9.]+)"
        assert extract_regex_field(pattern, text) == "8.7"

    def test_extract_regex_field_multiline(self):
        """Test extraction from multiline text."""
        text = "Título: The Matrix\nAno: 1999\nImdb: 8.7"
        pattern = r"Ano:\s*(\d+)"
        assert extract_regex_field(pattern, text) == "1999"

    def test_extract_regex_field_with_group(self):
        """Test extraction with custom group number."""
        text = "Date: 2024-11-22"
        pattern = r"Date:\s*(\d{4})-(\d{2})-(\d{2})"
        assert extract_regex_field(pattern, text, group=2) == "11"
        assert extract_regex_field(pattern, text, group=3) == "22"

    def test_extract_regex_field_strips_whitespace(self):
        """Test that extracted field is stripped of whitespace."""
        text = "Título:  The Matrix  "
        pattern = r"Título:\s*(.+)"
        result = extract_regex_field(pattern, text)
        assert result == "The Matrix"


class TestExtractPosterUrl:
    """Test the extract_poster_url function."""

    def test_extract_poster_url_success(self):
        """Test successful poster URL extraction."""
        # The actual selector used: body > div:nth-child(3) > div > div.col-12.col-sm-8.col-lg-9.my-1 > img
        # Build HTML without whitespace to avoid whitespace nodes affecting nth-child
        html = '<html><body><div></div><div></div><div><div><div class="col-12 col-sm-8 col-lg-9 my-1"><img src="https://example.com/poster.jpg" /></div></div></div></body></html>'
        soup = BeautifulSoup(html, "html.parser")
        url = extract_poster_url(soup)
        assert url == "https://example.com/poster.jpg"

    def test_extract_poster_url_not_found(self):
        """Test poster extraction when element not found."""
        html = "<html><body><div>No poster here</div></body></html>"
        soup = BeautifulSoup(html, "html.parser")
        url = extract_poster_url(soup)
        assert url is None

    def test_extract_poster_url_no_src(self):
        """Test poster extraction when img has no src attribute."""
        html = '<html><body><div></div><div></div><div><div><div class="col-12 col-sm-8 col-lg-9 my-1"><img alt="poster" /></div></div></div></body></html>'
        soup = BeautifulSoup(html, "html.parser")
        url = extract_poster_url(soup)
        assert url is None


class TestExtractSinopse:
    """Test the extract_sinopse function."""

    def test_extract_sinopse_success(self):
        """Test successful synopsis extraction."""
        html = """
        <html>
            <body>
                <div id="sinopse">
                    <p>A great movie about hackers.</p>
                </div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        sinopse = extract_sinopse(soup)
        assert sinopse == "A great movie about hackers."

    def test_extract_sinopse_with_descricao_prefix(self):
        """Test synopsis extraction removes 'Descrição:' prefix."""
        html = """
        <html>
            <body>
                <div id="sinopse">
                    <p>Descrição: A great movie about hackers.</p>
                </div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        sinopse = extract_sinopse(soup)
        assert sinopse == "A great movie about hackers."

    def test_extract_sinopse_not_found(self):
        """Test synopsis extraction when element not found."""
        html = "<html><body>No synopsis here</body></html>"
        soup = BeautifulSoup(html, "html.parser")
        sinopse = extract_sinopse(soup)
        assert sinopse is None

    def test_extract_sinopse_empty(self):
        """Test synopsis extraction with empty element."""
        html = """
        <html>
            <body>
                <div id="sinopse">
                    <p></p>
                </div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        sinopse = extract_sinopse(soup)
        assert sinopse == ""

    def test_extract_sinopse_with_colon_prefix(self):
        """Test synopsis extraction removes colon prefix."""
        html = """
        <html>
            <body>
                <div id="sinopse">
                    <p>Descrição: A great movie</p>
                </div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        sinopse = extract_sinopse(soup)
        assert sinopse == "A great movie"


class TestExtractMovieFields:
    """Test the extract_movie_fields function."""

    def test_extract_movie_fields_complete(self):
        """Test extraction of all fields from complete info text."""
        info_text = """
        Baixar The Matrix Torrent
        Título Original: The Matrix
        Imdb: 8.7 / 10
        Lançamento: 1999
        Gêneros: Sci-Fi, Action Idioma: English
        Tamanho: 2.5 GB
        Duração: 136 Minutos
        Vídeo: 1080 | H.264
        Qualidade: 1080p BluRay
        """
        fields = extract_movie_fields(info_text)

        assert fields["titulo_dublado"] == "The Matrix"
        assert fields["titulo_original"] == "The Matrix"
        assert fields["imdb"] == "8.7"
        assert fields["ano"] == "1999"
        assert "Sci-Fi" in fields["genero"]
        assert fields["tamanho"] == "2.5"
        assert fields["duracao_minutos"] == "136"
        assert fields["qualidade_video"] == "1080"
        assert "1080p" in fields["qualidade"]

    def test_extract_movie_fields_partial(self):
        """Test extraction when some fields are missing."""
        info_text = """
        Baixar Inception Torrent
        Título Original: Inception
        Imdb: 8.8 / 10
        """
        fields = extract_movie_fields(info_text)

        assert fields["titulo_dublado"] == "Inception"
        assert fields["titulo_original"] == "Inception"
        assert fields["imdb"] == "8.8"
        # Missing fields should be None
        assert fields["ano"] is None
        assert fields["genero"] is None

    def test_extract_movie_fields_none_values(self):
        """Test that missing patterns return None."""
        info_text = "Empty info text with no patterns"
        fields = extract_movie_fields(info_text)

        for value in fields.values():
            assert value is None


class TestCreateMovieObject:
    """Test the create_movie_object function."""

    def test_create_movie_object_success(self):
        """Test successful movie object creation."""
        extracted = {
            "titulo_dublado": "Origem",
            "titulo_original": "Inception",
            "imdb": "8.8",
            "ano": "2010",
            "genero": "Sci-Fi, Action",
            "tamanho": "2.5",
            "duracao_minutos": "148",
            "qualidade_video": "10",
            "qualidade": "1080p BluRay",
        }

        movie = create_movie_object(
            extracted,
            "Português",
            "A great movie",
            "https://example.com/inception",
            "https://example.com/poster.jpg",
        )

        assert movie is not None
        assert movie.titulo_original == "Inception"
        assert movie.imdb == 8.8
        assert movie.ano == 2010
        assert movie.dublado is True

    def test_create_movie_object_invalid_imdb(self):
        """Test movie creation with invalid IMDB rating."""
        extracted = {
            "titulo_dublado": "Test",
            "titulo_original": "Test Movie",
            "imdb": "11.0",  # Invalid: > 10
            "ano": "2020",
            "genero": None,
            "tamanho": None,
            "duracao_minutos": None,
            "qualidade_video": None,
            "qualidade": None,
        }

        movie = create_movie_object(
            extracted,
            "",
            None,
            "https://example.com/test",
            None,
        )

        assert movie is None

    def test_create_movie_object_invalid_year(self):
        """Test movie creation with invalid year."""
        extracted = {
            "titulo_dublado": "Test",
            "titulo_original": "Test Movie",
            "imdb": "8.0",
            "ano": "1887",  # Invalid: < 1888
            "genero": None,
            "tamanho": None,
            "duracao_minutos": None,
            "qualidade_video": None,
            "qualidade": None,
        }

        movie = create_movie_object(
            extracted,
            "",
            None,
            "https://example.com/test",
            None,
        )

        assert movie is None

    def test_create_movie_object_english_not_dubbed(self):
        """Test that movies without Portuguese are marked as not dubbed."""
        extracted = {
            "titulo_dublado": "Inception",
            "titulo_original": "Inception",
            "imdb": "8.8",
            "ano": "2010",
            "genero": None,
            "tamanho": None,
            "duracao_minutos": None,
            "qualidade_video": None,
            "qualidade": None,
        }

        movie = create_movie_object(
            extracted,
            "Inglês",  # English, not Portuguese
            None,
            "https://example.com/inception",
            None,
        )

        assert movie is not None
        assert movie.dublado is False


class TestParseMoviePage:
    """Test the parse_movie_page function."""

    def test_parse_movie_page_complete(self):
        """Test parsing a complete movie page."""
        html = """
        <html>
            <body>
                <div id="informacoes">
                    <p>
                        Baixar The Matrix Torrent
                        Título Original: The Matrix
                        Imdb: 8.7 / 10
                        Lançamento: 1999
                        Gêneros: Sci-Fi, Action Idioma: English
                        Tamanho: 2.5 GB
                        Duração: 136 Minutos
                        Vídeo: 1080 | H.264
                        Qualidade: 1080p BluRay
                        Português
                    </p>
                </div>
                <div id="sinopse">
                    <p>A hacker discovers reality is a simulation.</p>
                </div>
                <div><div><div class="col-12 col-sm-8 col-lg-9 my-1">
                    <img src="https://example.com/poster.jpg" />
                </div></div></div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        movie = parse_movie_page(soup, "https://example.com/matrix")

        assert movie is not None
        assert movie.titulo_original == "The Matrix"
        assert movie.ano == 1999
        assert movie.dublado is True

    def test_parse_movie_page_no_info_section(self):
        """Test parsing page with no info section."""
        html = "<html><body>No info here</body></html>"
        soup = BeautifulSoup(html, "html.parser")
        movie = parse_movie_page(soup, "https://example.com/test")

        assert movie is None

    def test_parse_movie_page_with_newlines(self):
        """Test parsing info text with newlines."""
        html = """
        <html>
            <body>
                <div id="informacoes">
                    <p>
                        Baixar Test Torrent
                        Título Original: Test Movie
                        Imdb:
                        8.5 / 10
                        Lançamento: 2020
                    </p>
                </div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        movie = parse_movie_page(soup, "https://example.com/test")

        assert movie is not None
