"""HTML fixtures for GratisTorrent scraper tests."""

from bs4 import BeautifulSoup

# Complete movie page with all fields
COMPLETE_MOVIE_PAGE_HTML = """
<html>
    <head><title>Inception</title></head>
    <body>
        <div class="sinopse">
            <h1 class="titulo">Inception</h1>
            <span class="titulo-dublado">Origem</span>
            <span class="rating">8.8</span>
            <span class="ano">2010</span>
            <span class="genero">Sci-Fi, Action, Thriller</span>
            <span class="downloads">5000</span>
            <span class="diretor">Christopher Nolan</span>
            <a href="magnet:?xt=urn:btih:123456789">Magnet Link</a>
        </div>
    </body>
</html>
"""

# Minimal movie page (missing most fields)
MINIMAL_MOVIE_PAGE_HTML = """
<html>
    <head><title>Movie</title></head>
    <body>
        <div class="sinopse">
            <h1 class="titulo">Some Movie</h1>
            <a href="magnet:?xt=urn:btih:abcdef">Magnet Link</a>
        </div>
    </body>
</html>
"""

# Movie page with special characters
SPECIAL_CHARS_MOVIE_PAGE_HTML = """
<html>
    <head><title>Café & Cigarettes</title></head>
    <body>
        <div class="sinopse">
            <h1 class="titulo">Café & Cigarettes</h1>
            <span class="titulo-dublado">Café & Cigarro - O Filme</span>
            <span class="rating">7.5</span>
            <span class="ano">2003</span>
            <span class="genero">Comedy, Drama</span>
            <a href="magnet:?xt=urn:btih:cafe123">Magnet Link</a>
        </div>
    </body>
</html>
"""

# Movie page with missing/malformed fields
MALFORMED_MOVIE_PAGE_HTML = """
<html>
    <head><title>Bad Movie</title></head>
    <body>
        <div class="sinopse">
            <h1 class="titulo">Bad Movie</h1>
            <span class="rating">invalid_rating</span>
            <span class="ano">not_a_year</span>
            <span class="downloads">abc downloads</span>
            <a href="bad_magnet_link">Not a magnet link</a>
        </div>
    </body>
</html>
"""

# Listing page with multiple movie links
LISTING_PAGE_WITH_LINKS_HTML = """
<html>
    <head><title>Latest Movies</title></head>
    <body>
        <div id="capas_pequenas">
            <div><a href="https://example.com/movie1">Movie 1</a></div>
            <div><a href="https://example.com/movie2">Movie 2</a></div>
            <div><a href="https://example.com/movie3">Movie 3</a></div>
            <div><a href="https://example.com/movie4">Movie 4</a></div>
            <div><a href="https://example.com/movie5">Movie 5</a></div>
        </div>
    </body>
</html>
"""

# Listing page with duplicate links
LISTING_PAGE_WITH_DUPLICATES_HTML = """
<html>
    <head><title>Latest Movies</title></head>
    <body>
        <div id="capas_pequenas">
            <div><a href="https://example.com/movie1">Movie 1</a></div>
            <div><a href="https://example.com/movie1">Movie 1 (Copy)</a></div>
            <div><a href="https://example.com/movie2">Movie 2</a></div>
            <div><a href="https://example.com/movie2">Movie 2 (Copy)</a></div>
            <div><a href="https://example.com/movie3">Movie 3</a></div>
        </div>
    </body>
</html>
"""

# Empty listing page
EMPTY_LISTING_PAGE_HTML = """
<html>
    <head><title>Latest Movies</title></head>
    <body>
        <div id="capas_pequenas">
        </div>
    </body>
</html>
"""

# Broken listing page structure
BROKEN_LISTING_PAGE_HTML = """
<html>
    <head><title>Latest Movies</title></head>
    <body>
        <div id="wrong_id">
            <div><a href="https://example.com/movie1">Movie 1</a></div>
        </div>
    </body>
</html>
"""


# Helper functions to get parsed objects
def get_complete_movie_soup() -> BeautifulSoup:
    """Return parsed complete movie page."""
    return BeautifulSoup(COMPLETE_MOVIE_PAGE_HTML, "html.parser")


def get_minimal_movie_soup() -> BeautifulSoup:
    """Return parsed minimal movie page."""
    return BeautifulSoup(MINIMAL_MOVIE_PAGE_HTML, "html.parser")


def get_special_chars_movie_soup() -> BeautifulSoup:
    """Return parsed special characters movie page."""
    return BeautifulSoup(SPECIAL_CHARS_MOVIE_PAGE_HTML, "html.parser")


def get_malformed_movie_soup() -> BeautifulSoup:
    """Return parsed malformed movie page."""
    return BeautifulSoup(MALFORMED_MOVIE_PAGE_HTML, "html.parser")


def get_listing_with_links_soup() -> BeautifulSoup:
    """Return parsed listing page with multiple links."""
    return BeautifulSoup(LISTING_PAGE_WITH_LINKS_HTML, "html.parser")


def get_listing_with_duplicates_soup() -> BeautifulSoup:
    """Return parsed listing page with duplicate links."""
    return BeautifulSoup(LISTING_PAGE_WITH_DUPLICATES_HTML, "html.parser")


def get_empty_listing_soup() -> BeautifulSoup:
    """Return parsed empty listing page."""
    return BeautifulSoup(EMPTY_LISTING_PAGE_HTML, "html.parser")


def get_broken_listing_soup() -> BeautifulSoup:
    """Return parsed broken listing page."""
    return BeautifulSoup(BROKEN_LISTING_PAGE_HTML, "html.parser")
