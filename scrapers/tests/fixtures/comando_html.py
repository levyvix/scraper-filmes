"""HTML fixtures for Comando Torrents scraper tests."""

from bs4 import BeautifulSoup

# Complete movie page with all fields
COMPLETE_MOVIE_PAGE_HTML = """
<html>
    <body>
        <div class="torrent-item">
            <h3 class="titulo">The Dark Knight</h3>
            <span class="titulo-dublado">O Cavaleiro das Trevas</span>
            <span class="rating">9.0</span>
            <span class="ano">2008</span>
            <span class="genero">Action, Crime, Drama</span>
            <span class="seeds">1000</span>
            <span class="peers">500</span>
            <span class="tamanho">2.5 GB</span>
            <a href="https://example.com/dark-knight" class="torrent-link">Download</a>
            <a href="magnet:?xt=urn:btih:darkknight123">Magnet</a>
        </div>
    </body>
</html>
"""

# Minimal movie page (missing most fields)
MINIMAL_MOVIE_PAGE_HTML = """
<html>
    <body>
        <div class="torrent-item">
            <h3 class="titulo">Some Movie</h3>
            <a href="https://example.com/movie" class="torrent-link">Download</a>
        </div>
    </body>
</html>
"""

# Movie page with special characters
SPECIAL_CHARS_MOVIE_PAGE_HTML = """
<html>
    <body>
        <div class="torrent-item">
            <h3 class="titulo">Shrek 4: Happily Ever After</h3>
            <span class="rating">6.2</span>
            <span class="ano">2010</span>
            <span class="genero">Animation, Adventure, Comedy</span>
            <span class="seeds">500</span>
            <span class="peers">200</span>
            <a href="https://example.com/shrek4" class="torrent-link">Download</a>
        </div>
    </body>
</html>
"""

# Movie page with missing/malformed fields
MALFORMED_MOVIE_PAGE_HTML = """
<html>
    <body>
        <div class="torrent-item">
            <h3 class="titulo">Bad Movie</h3>
            <span class="rating">invalid_rating</span>
            <span class="ano">not_a_year</span>
            <span class="seeds">abc_seeds</span>
            <span class="peers">xyz_peers</span>
            <a href="not_a_url" class="torrent-link">Bad Link</a>
        </div>
    </body>
</html>
"""

# Listing page with multiple movie torrents
LISTING_PAGE_WITH_TORRENTS_HTML = """
<html>
    <body>
        <div class="search-results">
            <div class="torrent-item">
                <h3 class="titulo">Movie 1</h3>
                <a href="https://example.com/movie1" class="torrent-link">Download</a>
            </div>
            <div class="torrent-item">
                <h3 class="titulo">Movie 2</h3>
                <a href="https://example.com/movie2" class="torrent-link">Download</a>
            </div>
            <div class="torrent-item">
                <h3 class="titulo">Movie 3</h3>
                <a href="https://example.com/movie3" class="torrent-link">Download</a>
            </div>
            <div class="torrent-item">
                <h3 class="titulo">Movie 4</h3>
                <a href="https://example.com/movie4" class="torrent-link">Download</a>
            </div>
            <div class="torrent-item">
                <h3 class="titulo">Movie 5</h3>
                <a href="https://example.com/movie5" class="torrent-link">Download</a>
            </div>
        </div>
    </body>
</html>
"""

# Listing page with duplicate torrents
LISTING_PAGE_WITH_DUPLICATES_HTML = """
<html>
    <body>
        <div class="search-results">
            <div class="torrent-item">
                <h3 class="titulo">Movie 1</h3>
                <a href="https://example.com/movie1" class="torrent-link">Download</a>
            </div>
            <div class="torrent-item">
                <h3 class="titulo">Movie 1 (Copy)</h3>
                <a href="https://example.com/movie1" class="torrent-link">Download</a>
            </div>
            <div class="torrent-item">
                <h3 class="titulo">Movie 2</h3>
                <a href="https://example.com/movie2" class="torrent-link">Download</a>
            </div>
            <div class="torrent-item">
                <h3 class="titulo">Movie 2 (Copy)</h3>
                <a href="https://example.com/movie2" class="torrent-link">Download</a>
            </div>
        </div>
    </body>
</html>
"""

# Empty listing page
EMPTY_LISTING_PAGE_HTML = """
<html>
    <body>
        <div class="search-results">
        </div>
    </body>
</html>
"""

# Broken listing page structure
BROKEN_LISTING_PAGE_HTML = """
<html>
    <body>
        <div class="wrong_container">
            <div class="torrent-item">
                <h3 class="titulo">Movie 1</h3>
                <a href="https://example.com/movie1" class="torrent-link">Download</a>
            </div>
        </div>
    </body>
</html>
"""

# Page with Cloudflare protection (incomplete/requires bypass)
CLOUDFLARE_PROTECTED_PAGE_HTML = """
<html>
    <body>
        <div id="cf-content">
            <h1>Please enable JavaScript</h1>
            <p>This site requires JavaScript to work properly.</p>
        </div>
    </body>
</html>
"""

# High quality torrent with full metadata
HIGH_QUALITY_TORRENT_HTML = """
<html>
    <body>
        <div class="torrent-item">
            <h3 class="titulo">Inception 4K Dual Audio</h3>
            <span class="rating">8.8</span>
            <span class="ano">2010</span>
            <span class="genero">Sci-Fi, Action, Thriller</span>
            <span class="seeds">5000</span>
            <span class="peers">2000</span>
            <span class="tamanho">8.5 GB</span>
            <span class="qualidade">4K Ultra HD</span>
            <a href="https://example.com/inception-4k" class="torrent-link">Download</a>
            <a href="magnet:?xt=urn:btih:inception4k">Magnet</a>
        </div>
    </body>
</html>
"""

# Low quality torrent with minimal metadata
LOW_QUALITY_TORRENT_HTML = """
<html>
    <body>
        <div class="torrent-item">
            <h3 class="titulo">Old Movie</h3>
            <span class="seeds">1</span>
            <span class="peers">0</span>
            <a href="https://example.com/old-movie" class="torrent-link">Download</a>
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


def get_listing_with_torrents_soup() -> BeautifulSoup:
    """Return parsed listing page with multiple torrents."""
    return BeautifulSoup(LISTING_PAGE_WITH_TORRENTS_HTML, "html.parser")


def get_listing_with_duplicates_soup() -> BeautifulSoup:
    """Return parsed listing page with duplicate torrents."""
    return BeautifulSoup(LISTING_PAGE_WITH_DUPLICATES_HTML, "html.parser")


def get_empty_listing_soup() -> BeautifulSoup:
    """Return parsed empty listing page."""
    return BeautifulSoup(EMPTY_LISTING_PAGE_HTML, "html.parser")


def get_broken_listing_soup() -> BeautifulSoup:
    """Return parsed broken listing page."""
    return BeautifulSoup(BROKEN_LISTING_PAGE_HTML, "html.parser")


def get_cloudflare_protected_soup() -> BeautifulSoup:
    """Return parsed Cloudflare protected page."""
    return BeautifulSoup(CLOUDFLARE_PROTECTED_PAGE_HTML, "html.parser")


def get_high_quality_torrent_soup() -> BeautifulSoup:
    """Return parsed high quality torrent page."""
    return BeautifulSoup(HIGH_QUALITY_TORRENT_HTML, "html.parser")


def get_low_quality_torrent_soup() -> BeautifulSoup:
    """Return parsed low quality torrent page."""
    return BeautifulSoup(LOW_QUALITY_TORRENT_HTML, "html.parser")
