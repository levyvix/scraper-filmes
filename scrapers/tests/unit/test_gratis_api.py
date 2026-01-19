"""Tests for scrapers.gratis_torrent package public API."""


class TestGratisTorrentPackageAPI:
    """Test that public API is properly exported from scrapers.gratis_torrent."""

    def test_import_scrape_function(self):
        """Test that scrape_all_movies can be imported."""
        from scrapers.gratis_torrent import scrape_all_movies

        assert callable(scrape_all_movies)

    def test_import_config_class(self):
        """Test that GratisTorrentConfig can be imported."""
        from scrapers.gratis_torrent import GratisTorrentConfig

        assert GratisTorrentConfig is not None

    def test_import_movie_model(self):
        """Test that Movie model can be imported."""
        from scrapers.gratis_torrent import Movie

        assert Movie is not None

    def test_import_flow(self):
        """Test that gratis_torrent_flow can be imported."""
        from scrapers.gratis_torrent import gratis_torrent_flow

        assert callable(gratis_torrent_flow)

    def test_import_bigquery_functions(self):
        """Test that BigQuery functions can be imported."""
        from scrapers.gratis_torrent import load_movies_to_bigquery

        assert callable(load_movies_to_bigquery)

    def test_import_http_client_functions(self):
        """Test that HTTP client functions can be imported."""
        from scrapers.gratis_torrent import collect_movie_links, fetch_page

        assert callable(fetch_page)
        assert callable(collect_movie_links)

    def test_all_attribute_exists(self):
        """Test that __all__ is defined in gratis_torrent package."""
        from scrapers import gratis_torrent

        assert hasattr(gratis_torrent, "__all__")
        assert isinstance(gratis_torrent.__all__, (list, tuple))
        assert len(gratis_torrent.__all__) > 0
