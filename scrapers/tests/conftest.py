import pytest
from pathlib import Path


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
