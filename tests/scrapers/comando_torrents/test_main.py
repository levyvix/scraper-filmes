import pytest
from unittest.mock import MagicMock, patch

from scrapers.comando_torrents.parser import (
    extract_text_or_none,
    safe_list_get,
    parse_detail,
)
from scrapers.comando_torrents.scraper import (
    get_movie_links,
)


class MockPage:
    def __init__(self, html_content, url):
        self.html_content = html_content
        self.url = url


# Mock external dependencies
@pytest.fixture
def mock_config():
    with patch("scrapers.comando_torrents.config.Config") as MockConfig:
        mock_instance = MockConfig.return_value
        mock_instance.base_url = "http://test.com"
        mock_instance.search_url = "http://test.com/search?q={}"
        mock_instance.output_path = "output.json"
        yield mock_instance


@pytest.fixture
def mock_stealthy_session():
    with patch("scrapers.comando_torrents.scraper.StealthySession") as MockSession:
        mock_session_instance = MockSession.return_value
        mock_session_instance.fetch.return_value = MockPage(
            html_content="<html><body>Test</body></html>", url="http://test.com"
        )
        yield mock_session_instance


@pytest.fixture
def mock_cache_memoize():
    # Disable cache.memoize for testing fetch_page_html directly
    with patch("scrapers.comando_torrents.scraper.cache.memoize", lambda f: f):
        yield


@pytest.fixture
def mock_adaptor():
    with patch("scrapers.comando_torrents.scraper.Adaptor") as MockAdaptor:
        mock_adaptor_instance = MockAdaptor.return_value
        yield mock_adaptor_instance


@pytest.fixture
def mock_cache():
    with patch("scrapers.comando_torrents.scraper.Cache") as MockCache:
        mock_cache_instance = MockCache.return_value
        yield mock_cache_instance


# Unit tests for extract_text_or_none
def test_extract_text_or_none_success():
    mock_element = MagicMock()
    mock_css_first_result = MagicMock()
    mock_css_first_result.__str__.return_value = "Extracted Text"
    mock_element.css_first.return_value = mock_css_first_result
    text = extract_text_or_none(mock_element, "selector")
    assert text == "Extracted Text"


def test_extract_text_or_none_no_element():
    mock_element = MagicMock()
    mock_element.css_first.return_value = None
    text = extract_text_or_none(mock_element, "selector")
    assert text is None


def test_extract_text_or_none_no_text():
    mock_element = MagicMock()
    mock_css_first_result = MagicMock()
    mock_css_first_result.__str__.return_value = ""
    mock_element.css_first.return_value = mock_css_first_result
    text = extract_text_or_none(mock_element, "selector")
    assert text is None


# Unit tests for safe_list_get
def test_safe_list_get_valid_index():
    test_list = [1, 2, 3]
    assert safe_list_get(test_list, 1) == 2


def test_safe_list_get_out_of_range():
    test_list = [1, 2, 3]
    assert safe_list_get(test_list, 5) == ""


def test_safe_list_get_empty_list():
    test_list = []
    assert safe_list_get(test_list, 0) == ""


# Unit tests for parse_detail
@patch("scrapers.comando_torrents.parser.fetch_page")
def test_parse_detail_success(mock_fetch_page):
    mock_adaptor_instance = MagicMock()
    mock_adaptor_instance.css.side_effect = [
        [
            "Titulo Dublado: Movie Title",  # index 0
            "Titulo Original: Original Title",  # index 1
            "IMDB: 7.0",  # index 2
            "2020",  # index 3
            "Genre",  # index 4
            "Size",  # index 5
            "Quality: 1080p",  # index 6 (qualidade)
            "Audio: Português",  # index 7
            "Video Quality: 7.0",  # index 8
            "Extra Info",  # index 9
            "Duration: 120 min",  # index 10 (duracao)
            "Video Quality: 7.0",  # index 11
        ],
        ["Synopsis"],  # For sinopse_list
    ]
    mock_adaptor_instance.css_first.side_effect = [
        MagicMock(text="7.0"),  # For imdb_text
        MagicMock(text="2020"),  # For year_text
        MagicMock(__str__=lambda x: "image.jpg", attributes={"src": "image.jpg"}),  # For poster_url_result
    ]
    mock_fetch_page.return_value = mock_adaptor_instance

    movie = parse_detail("http://test.com/movie")

    assert movie is not None
    # "Titulo Dublado: Movie Title".replace(":", "").strip() = "Titulo Dublado Movie Title"
    assert movie.titulo_dublado == "Titulo Dublado Movie Title"
    assert movie.ano == 2020
    # safe_list_get returns "Quality: 1080p" and .strip() doesn't remove the label
    assert movie.qualidade == "Quality: 1080p"
    assert movie.link == "http://test.com/movie"
    assert movie.dublado


@patch("scrapers.comando_torrents.parser.fetch_page")
def test_parse_detail_fetch_page_fails(mock_fetch_page):
    mock_fetch_page.return_value = None
    movie = parse_detail("http://test.com/movie")
    assert movie is None


@patch("scrapers.comando_torrents.parser.fetch_page")
def test_parse_detail_validation_error(mock_fetch_page):
    mock_page_content = MagicMock()
    mock_page_content.css.return_value = []  # Simulate incomplete data
    mock_fetch_page.return_value = mock_page_content

    movie = parse_detail("http://test.com/movie")
    assert movie is None


# Unit tests for get_movie_links
@patch("scrapers.comando_torrents.scraper.fetch_page")
def test_get_movie_links_success(mock_fetch_page):
    mock_page_content = MagicMock()
    mock_page_content.css.return_value = ["http://test.com/movie1", "http://test.com/movie2"]
    mock_fetch_page.return_value = mock_page_content

    links = get_movie_links("http://test.com/search")
    assert links == ["http://test.com/movie1", "http://test.com/movie2"]


@patch("scrapers.comando_torrents.scraper.fetch_page")
def test_get_movie_links_fetch_page_fails(mock_fetch_page):
    mock_fetch_page.side_effect = Exception("Network error")
    links = get_movie_links("http://test.com/search")
    assert links == []


@patch("scrapers.comando_torrents.scraper.fetch_page")
def test_get_movie_links_no_links_found(mock_fetch_page):
    mock_page_content = MagicMock()
    mock_page_content.css.return_value = []
    mock_fetch_page.return_value = mock_page_content
    links = get_movie_links("http://test.com/search")
    assert links == []
