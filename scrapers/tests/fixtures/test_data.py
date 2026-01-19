"""Reusable test data fixtures for movie objects and validation."""

from scrapers.gratis_torrent.models import Movie

# Valid movies with all fields
VALID_MOVIE_COMPLETE = Movie(
    titulo_original="Inception",
    titulo_dublado="Origem",
    link="https://example.com/inception",
    imdb=8.8,
    ano=2010,
    genero="Sci-Fi, Action",
    duracao="148 min",
    qualidade="1080p",
    qualidade_video=9.0,
    duracao_minutos=148,
)

VALID_MOVIE_MINIMAL = Movie(
    titulo_original="Interstellar",
    link="https://example.com/interstellar",
    imdb=8.6,
    ano=2014,
    duracao="169 min",
    qualidade="720p",
    qualidade_video=None,
    duracao_minutos=169,
)

# Movies with partial data (some None fields)
PARTIAL_MOVIE_NO_RATING = Movie(
    titulo_original="The Dark Knight",
    titulo_dublado="O Cavaleiro das Trevas",
    link="https://example.com/dark-knight",
    ano=2008,
    genero="Action, Crime",
    imdb=None,  # Missing IMDB
    duracao="152 min",
    qualidade="1080p",
    qualidade_video=None,
    duracao_minutos=152,
)

PARTIAL_MOVIE_NO_YEAR = Movie(
    titulo_original="Pulp Fiction",
    link="https://example.com/pulp-fiction",
    imdb=8.9,
    genero="Crime, Drama",
    titulo_dublado="Dança com Lobos",
    ano=None,  # Missing year
    duracao="154 min",
    qualidade="1080p",
    qualidade_video=None,
    duracao_minutos=154,
)

# Movie with special characters
MOVIE_WITH_SPECIAL_CHARS = Movie(
    titulo_original="Café & Cigarettes",
    titulo_dublado="Café & Cigarro - O Filme",
    link="https://example.com/cafe-cigarettes",
    imdb=7.5,
    ano=2003,
    genero="Comedy, Drama",
    duracao="120 min",
    qualidade="720p",
    qualidade_video=7.0,
    duracao_minutos=120,
)

# Boundary value movies
BOUNDARY_MOVIE_RATING_0 = Movie(
    titulo_original="Worst Movie",
    link="https://example.com/worst",
    imdb=0.0,  # Boundary minimum
    ano=2020,
    duracao="90 min",
    qualidade="480p",
    qualidade_video=None,
    duracao_minutos=90,
)

BOUNDARY_MOVIE_RATING_10 = Movie(
    titulo_original="Best Movie",
    link="https://example.com/best",
    imdb=10.0,  # Boundary maximum
    ano=2020,
    duracao="180 min",
    qualidade="4K",
    qualidade_video=10.0,
    duracao_minutos=180,
)

BOUNDARY_MOVIE_YEAR_1888 = Movie(
    titulo_original="First Ever",
    link="https://example.com/first",
    imdb=5.0,
    ano=1888,  # Boundary minimum year
    duracao="120 min",
    qualidade="Original",
    qualidade_video=None,
    duracao_minutos=120,
)

# List of all valid movies
VALID_MOVIES = [
    VALID_MOVIE_COMPLETE,
    VALID_MOVIE_MINIMAL,
    PARTIAL_MOVIE_NO_RATING,
    PARTIAL_MOVIE_NO_YEAR,
    MOVIE_WITH_SPECIAL_CHARS,
    BOUNDARY_MOVIE_RATING_0,
    BOUNDARY_MOVIE_RATING_10,
    BOUNDARY_MOVIE_YEAR_1888,
]


# Lazy-loaded invalid movie data (can't be instantiated due to Pydantic validation)
# These are used in tests that verify validation rejects bad data
def get_invalid_movie_data():
    """Return list of raw data dicts for invalid movies (fail validation)."""
    return [
        {
            "titulo_original": "Invalid High",
            "link": "https://example.com/invalid-high",
            "imdb": 10.5,  # IMDB max is 10
            "ano": 2020,
        },
        {
            "titulo_original": "Invalid Negative",
            "link": "https://example.com/invalid-neg",
            "imdb": -1.0,  # Negative IMDB
            "ano": 2020,
        },
        {
            "titulo_original": "Too Old",
            "link": "https://example.com/too-old",
            "imdb": 8.0,
            "ano": 1887,  # Before 1888
        },
    ]
