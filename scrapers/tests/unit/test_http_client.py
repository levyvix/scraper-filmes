from bs4 import BeautifulSoup
from scrapers.gratis_torrent.http_client import collect_movie_links


def test_collect_movie_links():
    """Test the collect_movie_links function with mock HTML."""
    html = """
    <html>
        <div id="capas_pequenas">
            <div><a href="https://example.com/movie1">Movie 1</a></div>
            <div><a href="https://example.com/movie2">Movie 2</a></div>
            <div><a href="https://example.com/movie1">Movie 1 Again</a></div>
        </div>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    links = collect_movie_links(soup)

    assert len(links) == 2
    assert "https://example.com/movie1" in links
    assert "https://example.com/movie2" in links
