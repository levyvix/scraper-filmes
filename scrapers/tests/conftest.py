import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest


def pytest_configure(config):
    """Configure pytest before test collection.

    This hook runs BEFORE test collection, allowing us to mock problematic imports.
    The Scrapling library requires camoufox browser binary which isn't available in test environments.
    """
    # Mock camoufox (browser automation) - needed before scrapling imports
    camoufox_mock = MagicMock()
    camoufox_mock.__path__ = []
    sys.modules["camoufox"] = camoufox_mock

    pkgman_mock = MagicMock()
    pkgman_mock.__path__ = []
    version_mock = MagicMock()
    version_mock.from_path = MagicMock(
        side_effect=FileNotFoundError("Version info not found")
    )
    pkgman_mock.Version = version_mock
    sys.modules["camoufox.pkgman"] = pkgman_mock

    # Mock scrapling (web scraping library with browser support)
    scrapling_mock = MagicMock()
    scrapling_mock.__path__ = []

    engines_mock = MagicMock()
    engines_mock.__path__ = []
    sys.modules["scrapling.engines"] = engines_mock

    browsers_mock = MagicMock()
    browsers_mock.__path__ = []
    sys.modules["scrapling.engines._browsers"] = browsers_mock

    camoufox_browsers_mock = MagicMock()
    camoufox_browsers_mock.__path__ = []
    sys.modules["scrapling.engines._browsers._camoufox"] = camoufox_browsers_mock

    base_mock = MagicMock()
    base_mock.__path__ = []
    sys.modules["scrapling.engines._browsers._base"] = base_mock

    fetchers_mock = MagicMock()
    fetchers_mock.__path__ = []
    fetchers_mock.StealthySession = MagicMock()
    sys.modules["scrapling.fetchers"] = fetchers_mock

    firefox_mock = MagicMock()
    firefox_mock.__path__ = []
    sys.modules["scrapling.fetchers.firefox"] = firefox_mock

    parser_mock = MagicMock()
    parser_mock.__path__ = []

    # Create a real Adaptor class for isinstance checks in tests
    class Adaptor:
        def __init__(self, html, url):
            self.html = html
            self.url = url

        def css(self, selector):
            return []

    parser_mock.Adaptor = Adaptor
    sys.modules["scrapling.parser"] = parser_mock

    sys.modules["scrapling"] = scrapling_mock


@pytest.fixture
def sample_gratis_html():
    """Load sample HTML for gratis_torrent tests."""
    fixture_path = Path(__name__).parent / "fixtures" / "sample_gratis.html"
    return fixture_path.read_text()


@pytest.fixture
def mock_movie_data():
    """Sample movie data for testing."""
    return {
        "titulo_dublado": "Matrix",
        "titulo_original": "The Matrix",
        "imdb": 8.7,
        "ano": 1999,
        "genero": "Action, Sci-Fi",
        "tamanho": "2.5",
        "duracao_minutos": 136,
        "qualidade_video": 10.0,
        "qualidade": "1080p BluRay",
        "dublado": True,
        "sinopse": "A hacker discovers reality.",
        "link": "https://example.com/matrix",
    }
