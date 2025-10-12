"""Tests for models module."""

import pytest
from pydantic import ValidationError

from src.scrapers.gratis_torrent.models import Movie


class TestMovie:
    """Tests for Movie model."""

    def test_create_valid_movie(self):
        """Test creating a valid movie."""
        movie = Movie(
            titulo_dublado="The Matrix",
            titulo_original="The Matrix",
            imdb=8.7,
            ano=1999,
            genero="Action, Sci-Fi",
            tamanho="2.5",
            duracao_minutos=136,
            qualidade_video=10.0,
            qualidade="1080p BluRay",
            dublado=True,
            sinopse="A computer hacker learns about reality.",
            link="https://example.com/matrix",
        )

        assert movie.titulo_dublado == "The Matrix"
        assert movie.imdb == 8.7
        assert movie.ano == 1999
        assert movie.dublado is True

    def test_create_movie_with_none_values(self):
        """Test creating movie with None values."""
        movie = Movie(
            titulo_dublado=None,
            titulo_original=None,
            imdb=None,
            ano=None,
            genero=None,
            tamanho=None,
            duracao_minutos=None,
            qualidade_video=None,
            qualidade=None,
            dublado=None,
            sinopse=None,
            link=None,
        )

        assert movie.titulo_dublado is None
        assert movie.imdb is None

    def test_imdb_validation_valid_range(self):
        """Test IMDB score within valid range."""
        movie = Movie(imdb=0.0)
        assert movie.imdb == 0.0

        movie = Movie(imdb=10.0)
        assert movie.imdb == 10.0

        movie = Movie(imdb=7.5)
        assert movie.imdb == 7.5

    def test_imdb_validation_invalid_range(self):
        """Test IMDB score outside valid range."""
        with pytest.raises(ValidationError):
            Movie(imdb=-1.0)

        with pytest.raises(ValidationError):
            Movie(imdb=11.0)

    def test_ano_validation_valid_range(self):
        """Test year within valid range."""
        movie = Movie(ano=1888)
        assert movie.ano == 1888

        movie = Movie(ano=2024)
        assert movie.ano == 2024

    def test_ano_validation_invalid_range(self):
        """Test year outside valid range."""
        with pytest.raises(ValidationError):
            Movie(ano=1887)

    def test_duracao_minutos_validation(self):
        """Test duration validation."""
        movie = Movie(duracao_minutos=1)
        assert movie.duracao_minutos == 1

        movie = Movie(duracao_minutos=200)
        assert movie.duracao_minutos == 200

        with pytest.raises(ValidationError):
            Movie(duracao_minutos=0)

        with pytest.raises(ValidationError):
            Movie(duracao_minutos=-10)

    def test_qualidade_video_validation(self):
        """Test video quality validation."""
        movie = Movie(qualidade_video=0.0)
        assert movie.qualidade_video == 0.0

        movie = Movie(qualidade_video=10.0)
        assert movie.qualidade_video == 10.0

        with pytest.raises(ValidationError):
            Movie(qualidade_video=-1.0)

    def test_model_dump(self):
        """Test converting model to dictionary."""
        movie = Movie(
            titulo_dublado="The Matrix",
            ano=1999,
            imdb=8.7,
        )

        data = movie.model_dump()

        assert isinstance(data, dict)
        assert data["titulo_dublado"] == "The Matrix"
        assert data["ano"] == 1999
        assert data["imdb"] == 8.7
