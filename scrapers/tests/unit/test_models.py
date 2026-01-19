import pytest
from pydantic import ValidationError

from scrapers.gratis_torrent.models import Movie


def test_pydantic_valid_data(mock_movie_data):
    """Test that valid data creates a Movie instance."""
    # Remove fields that are not in the base model for this test
    mock_movie_data.pop("duracao_minutos")

    movie = Movie(**mock_movie_data, duracao=None)
    assert movie.titulo_dublado == "Matrix"
    assert movie.imdb == 8.7
    assert movie.ano == 1999


def test_pydantic_invalid_imdb():
    """Test that validation fails for an invalid IMDB score."""
    with pytest.raises(ValidationError):
        Movie(
            titulo_dublado="Teste",
            imdb=15.0,  # Invalid IMDB
            ano=2020,
            link="http://example.com",
        )


def test_pydantic_invalid_year():
    """Test that validation fails for an invalid year."""
    with pytest.raises(ValidationError):
        Movie(
            titulo_dublado="Teste",
            imdb=7.0,
            ano=1800,  # Invalid year
            link="http://example.com",
        )


def test_model_serialization(mock_movie_data):
    """Test the model_dump() serialization."""
    # Add the field specific to the gratis_torrent model
    mock_movie_data["duracao_minutos"] = 136

    movie = Movie(**mock_movie_data, duracao=None)
    data = movie.model_dump()

    assert isinstance(data, dict)
    assert data["titulo_dublado"] == "Matrix"
    assert data["imdb"] == 8.7
    assert data["ano"] == 1999

    required_fields = [
        "titulo_dublado",
        "titulo_original",
        "imdb",
        "ano",
        "genero",
        "tamanho",
        "duracao_minutos",
        "qualidade_video",
        "qualidade",
        "dublado",
        "sinopse",
        "link",
    ]

    for field in required_fields:
        assert field in data
        assert data[field] is not None
