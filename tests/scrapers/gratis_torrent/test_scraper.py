import pytest
from unittest.mock import MagicMock, patch
from src.scrapers.gratis_torrent.scraper import (
    scrape_movie_links,
    scrape_movie_details,
    scrape_all_movies,
)
from src.utils.models import Movie
from bs4 import BeautifulSoup


# Mock external dependencies
@pytest.fixture
def mock_config():
    with patch("src.scrapers.gratis_torrent.scraper.Config") as MockConfig:
        MockConfig.BASE_URL = "http://test.com/base"
        yield MockConfig


@pytest.fixture
def mock_fetch_page():
    with patch("src.scrapers.gratis_torrent.scraper.fetch_page") as mock:
        mock_soup = MagicMock(spec=BeautifulSoup)
        mock_a_tag1 = MagicMock()
        mock_a_tag1.get.return_value = "http://test.com/movie1"
        mock_a_tag2 = MagicMock()
        mock_a_tag2.get.return_value = "http://test.com/movie2"
        mock_soup.select.return_value = [mock_a_tag1, mock_a_tag2]
        mock.return_value = mock_soup
        yield mock


@pytest.fixture
def mock_parse_movie_page():
    with patch("src.scrapers.gratis_torrent.scraper.parse_movie_page") as mock:
        yield mock


# Unit tests for scrape_movie_links
def test_scrape_movie_links_success(mock_fetch_page, mock_config):
    mock_fetch_page.return_value.css.return_value = [
        MagicMock(attributes={"href": "/movie1"}),
        MagicMock(attributes={"href": "/movie2"}),
    ]

    links = scrape_movie_links()

    assert set(links) == set(["http://test.com/movie1", "http://test.com/movie2"])
    mock_fetch_page.assert_called_once_with(mock_config.BASE_URL)


def test_scrape_movie_links_fetch_page_fails(mock_fetch_page, mock_config):
    mock_fetch_page.return_value = None

    links = scrape_movie_links()

    assert links == []
    mock_fetch_page.assert_called_once_with(mock_config.BASE_URL)


def test_scrape_movie_links_no_links_found(mock_fetch_page, mock_config):
    mock_page_content = MagicMock()
    mock_page_content.css.return_value = []
    mock_fetch_page.return_value = mock_page_content

    links = scrape_movie_links()

    assert links == []
    mock_fetch_page.assert_called_once_with(mock_config.BASE_URL)


# Unit tests for scrape_movie_details
def test_scrape_movie_details_success(mock_fetch_page, mock_parse_movie_page):
    mock_page_content = MagicMock()
    mock_fetch_page.return_value = mock_page_content
    mock_parse_movie_page.return_value = Movie(
        titulo_dublado="Movie Title",
        ano=2023,
        imdb="8.0",
        sinopse="A great movie.",
        qualidade="1080p",
        poster_url="http://test.com/poster.jpg",
        link="http://test.com/movie",
        qualidade_video=8.0,
        dublado=True,
    )

    movie = scrape_movie_details("http://test.com/movie")

    assert movie.titulo_dublado == "Movie Title"
    mock_fetch_page.assert_called_once_with("http://test.com/movie")
    mock_parse_movie_page.assert_called_once_with(mock_page_content, "http://test.com/movie")


def test_scrape_movie_details_fetch_page_fails(mock_fetch_page, mock_parse_movie_page):
    mock_fetch_page.return_value = None

    movie = scrape_movie_details("http://test.com/movie")

    assert movie is None
    mock_fetch_page.assert_called_once_with("http://test.com/movie")
    mock_parse_movie_page.assert_not_called()


def test_scrape_movie_details_parse_movie_page_fails(mock_fetch_page, mock_parse_movie_page):
    mock_page_content = MagicMock()
    mock_fetch_page.return_value = mock_page_content
    mock_parse_movie_page.return_value = None

    movie = scrape_movie_details("http://test.com/movie")

    assert movie is None
    mock_fetch_page.assert_called_once_with("http://test.com/movie")
    mock_parse_movie_page.assert_called_once_with(mock_page_content, "http://test.com/movie")


@pytest.fixture(autouse=True)
def disable_cache_memoize():
    with patch("src.scrapers.gratis_torrent.scraper.cache.memoize", lambda f, *args, **kwargs: f):
        yield

# Unit tests for scrape_all_movies
@patch("src.scrapers.gratis_torrent.scraper.scrape_movie_links")
@patch("src.scrapers.gratis_torrent.scraper.scrape_movie_details")
def test_scrape_all_movies_success(mock_scrape_movie_details, mock_scrape_movie_links):
    mock_scrape_movie_links.return_value = ["http://test.com/movie1", "http://test.com/movie2"]
    mock_scrape_movie_details.side_effect = [
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
        ),
        None,  # Simulate a failed scrape
    ]

    movies = scrape_all_movies()

    assert len(movies) == 1
    assert movies[0]["titulo_dublado"] == "Movie 1"
    mock_scrape_movie_links.assert_called_once()
    assert mock_scrape_movie_details.call_count == 2


@patch("src.scrapers.gratis_torrent.scraper.scrape_movie_links")
@patch("src.scrapers.gratis_torrent.scraper.scrape_movie_details")
def test_scrape_all_movies_no_links(mock_scrape_movie_details, mock_scrape_movie_links):
    mock_scrape_movie_links.return_value = []

    movies = scrape_all_movies()

    assert len(movies) == 0
    mock_scrape_movie_links.assert_called_once()
    mock_scrape_movie_details.assert_not_called()


@patch("src.scrapers.gratis_torrent.scraper.scrape_movie_links")
@patch("src.scrapers.gratis_torrent.scraper.scrape_movie_details")
def test_scrape_all_movies_all_details_fail(mock_scrape_movie_details, mock_scrape_movie_links):
    mock_scrape_movie_links.return_value = ["http://test.com/movie1", "http://test.com/movie2"]
    mock_scrape_movie_details.return_value = None

    movies = scrape_all_movies()

    assert len(movies) == 0
    mock_scrape_movie_links.assert_called_once()
    assert mock_scrape_movie_details.call_count == 2
