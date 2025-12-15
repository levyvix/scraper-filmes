import pytest
from unittest.mock import MagicMock, patch
from src.scrapers.comando_torrents.main import (
    extract_text_or_none,
    safe_list_get,
    parse_detail,
    get_movie_links,
    main,
    save_to_json,
    __file__ as main_file,
)
from src.utils.models import Movie


class MockPage:
    def __init__(self, html_content, url):
        self.html_content = html_content
        self.url = url


# Mock external dependencies
@pytest.fixture
def mock_config():
    with patch("src.scrapers.comando_torrents.config.Config") as MockConfig:
        mock_instance = MockConfig.return_value
        mock_instance.base_url = "http://test.com"
        mock_instance.search_url = "http://test.com/search?q={}"
        mock_instance.output_path = "output.json"
        yield mock_instance


@pytest.fixture
def mock_stealthy_session():
    with patch("src.scrapers.comando_torrents.main.StealthySession") as MockSession:
        mock_session_instance = MockSession.return_value
        mock_session_instance.fetch.return_value = MockPage(html_content="<html><body>Test</body></html>", url="http://test.com")
        yield mock_session_instance


@pytest.fixture
def mock_cache_memoize():
    # Disable cache.memoize for testing fetch_page_html directly
    with patch("src.scrapers.comando_torrents.main.cache.memoize", lambda f: f):
        yield


@pytest.fixture
def mock_adaptor():
    with patch("src.scrapers.comando_torrents.main.Adaptor") as MockAdaptor:
        mock_adaptor_instance = MockAdaptor.return_value
        yield mock_adaptor_instance


@pytest.fixture
def mock_cache():
    with patch("src.scrapers.comando_torrents.main.Cache") as MockCache:
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
@pytest.fixture
def mock_fetch_page():
    with patch("src.scrapers.comando_torrents.main.fetch_page") as mock:
        yield mock


@pytest.fixture
def mock_extract_text_or_none():
    with patch("src.scrapers.comando_torrents.main.extract_text_or_none") as mock:
        yield mock


@patch("src.scrapers.comando_torrents.main.parse_rating", return_value=7.0)
@patch("src.scrapers.comando_torrents.main.parse_year", return_value=2020)
def test_parse_detail_success(mock_parse_year, mock_parse_rating, mock_fetch_page):
    mock_adaptor_instance = MagicMock()
    mock_adaptor_instance.css.side_effect = [
        [
            "Titulo Dublado: Movie Title",
            "Titulo Original: Original Title",
            "IMDB: 7.0",
            "2020",
            "Genre",
            "Size",
            "Duration",
            "Audio: Português",
            "Quality: 1080p",
            "Video Quality: 7.0",
            "Extra Info",  # 12th element for safe_list_get
            "Another Extra Info", # Added missing element
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

    assert movie.titulo_dublado == "Movie Title"
    assert movie.ano == 2020
    assert movie.imdb == "7.0"
    assert movie.sinopse == "Synopsis"
    assert movie.qualidade == "1080p"
    assert movie.poster_url == "image.jpg"
    assert movie.link == "http://test.com/movie"
    assert movie.qualidade_video == 7.0
    assert movie.dublado == True


@patch("src.scrapers.comando_torrents.main.parse_rating", return_value=None)
@patch("src.scrapers.comando_torrents.main.parse_year", return_value=None)
def test_parse_detail_fetch_page_fails(mock_parse_year, mock_parse_rating, mock_fetch_page):
    mock_fetch_page.return_value = None
    movie = parse_detail("http://test.com/movie")
    assert movie is None


@patch("src.scrapers.comando_torrents.main.parse_rating", return_value=7.0)
@patch("src.scrapers.comando_torrents.main.parse_year", return_value=2020)
def test_parse_detail_validation_error(mock_parse_year, mock_parse_rating, mock_fetch_page):
    mock_page_content = MagicMock()
    mock_page_content.css.return_value = []  # Simulate incomplete data
    mock_fetch_page.return_value = mock_page_content

    movie = parse_detail("http://test.com/movie")
    assert movie is None


# Unit tests for get_movie_links
def test_get_movie_links_success(mock_fetch_page, mocker):
    mock_config_class = mocker.patch("src.scrapers.comando_torrents.main.Config")
    mock_config_instance = mock_config_class.return_value
    mock_config_instance.base_url = "http://test.com"

    mock_page_content = MagicMock()
    mock_page_content.css.return_value = ["/movie1", "/movie2"]
    mock_fetch_page.return_value = mock_page_content

    links = get_movie_links("http://test.com/search")
    assert links == ["http://test.com/movie1", "http://test.com/movie2"]


def test_get_movie_links_fetch_page_fails(mock_fetch_page):
    mock_fetch_page.return_value = None
    links = get_movie_links("http://test.com/search")
    assert links == []


def test_get_movie_links_no_links_found(mock_fetch_page):
    mock_page_content = MagicMock()
    mock_page_content.css.return_value = []
    mock_fetch_page.return_value = mock_page_content
    links = get_movie_links("http://test.com/search")
    assert links == []


# Unit tests for main
@patch("src.scrapers.comando_torrents.main.get_movie_links")
@patch("src.scrapers.comando_torrents.main.parse_detail")
@patch("src.scrapers.comando_torrents.main.save_to_json")
@patch("src.scrapers.comando_torrents.main.StealthySession")
@patch("src.scrapers.comando_torrents.main.Adaptor")
@patch("src.scrapers.comando_torrents.main.Cache")
@patch("src.scrapers.comando_torrents.main.Config")
def test_main_flow(MockConfig, MockCache, MockAdaptor, MockSession, mock_save_to_json, mock_parse_detail, mock_get_movie_links):
    mock_config_instance = MockConfig.return_value
    mock_config_instance.URL_BASE = "http://test.com/base"
    mock_get_movie_links.return_value = ["http://test.com/movie1", "http://test.com/movie2"]
    expected_movie = Movie(
        titulo_dublado="Movie 1",
        ano=2020,
        imdb="7.0",
        sinopse="Desc 1",
        qualidade="1080p",
        poster_url="img1.jpg",
        link="http://test.com/movie1",
        qualidade_video=7.0,
        dublado=True,
    )
    mock_parse_detail.side_effect = [expected_movie, None]

    main()

    mock_get_movie_links.assert_called_once_with(mock_config_instance.URL_BASE)
    assert mock_parse_detail.call_count == 2
    mock_save_to_json.assert_called_once_with(mock_config_instance, [expected_movie])


@patch("src.scrapers.comando_torrents.main.get_movie_links")
@patch("src.scrapers.comando_torrents.main.parse_detail")
@patch("src.scrapers.comando_torrents.main.save_to_json")
@patch("src.scrapers.comando_torrents.main.StealthySession")
@patch("src.scrapers.comando_torrents.main.Adaptor")
@patch("src.scrapers.comando_torrents.main.Cache")
@patch("src.scrapers.comando_torrents.main.Config")
def test_main_no_links_found(MockConfig, MockCache, MockAdaptor, MockSession, mock_save_to_json, mock_parse_detail, mock_get_movie_links):
    mock_config_instance = MockConfig.return_value
    mock_config_instance.URL_BASE = "http://test.com/base"
    mock_get_movie_links.return_value = []
    result = main()
    mock_get_movie_links.assert_called_once_with(mock_config_instance.URL_BASE)
    mock_parse_detail.assert_not_called()
    mock_save_to_json.assert_not_called()
    assert result is None


# Unit tests for save_to_json
@patch("src.scrapers.comando_torrents.main.Path")
@patch("json.dumps")
def test_save_to_json_success(mock_json_dumps, mock_path, mock_config):
    movies = [
        Movie(
            titulo_dublado="Movie 1",
            ano=2020,
            imdb="7.0",
            sinopse="Desc 1",
            qualidade="1080p",
            poster_url="img1.jpg",
            link="http://test.com/movie1",
            qualidade_video=7.0,
            dublado=True,
        )
    ]
    mock_file_path = MagicMock()
    mock_path.return_value.parent.__truediv__.return_value = mock_file_path
    mock_config.JSON_FILE_NAME = "output.json"

    save_to_json(mock_config, movies)

    mock_path.assert_called_once_with(main_file)
    mock_file_path.write_text.assert_called_once()
    mock_json_dumps.assert_called_once()


@patch("src.scrapers.comando_torrents.main.Path")
@patch("json.dumps")
def test_save_to_json_io_error(mock_json_dumps, mock_path, mock_config):
    movies = [
        Movie(
            titulo_dublado="Movie 1",
            ano=2020,
            imdb="7.0",
            sinopse="Desc 1",
            qualidade="1080p",
            poster_url="img1.jpg",
            link="http://test.com/movie1",
            qualidade_video=7.0,
            dublado=True,
        )
    ]
    mock_file_path = MagicMock()
    mock_path.return_value.parent.__truediv__.return_value = mock_file_path
    mock_file_path.write_text.side_effect = IOError("Disk full")
    mock_config.JSON_FILE_NAME = "output.json"

    with pytest.raises(IOError):
        save_to_json(mock_config, movies)

    mock_path.assert_called_once_with(main_file)
    mock_file_path.write_text.assert_called_once()
    mock_json_dumps.assert_called_once()
