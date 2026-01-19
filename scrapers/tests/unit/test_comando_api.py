"""Tests for scrapers.comando_torrents package public API."""


class TestComandoTorrentsPackageAPI:
    """Test that public API is properly exported from scrapers.comando_torrents."""

    def test_import_get_movie_links_function(self):
        """Test that get_movie_links can be imported."""
        from scrapers.comando_torrents import get_movie_links

        assert callable(get_movie_links)

    def test_import_config_class(self):
        """Test that ComandoTorrentsConfig can be imported."""
        from scrapers.comando_torrents import ComandoTorrentsConfig

        assert ComandoTorrentsConfig is not None

    def test_import_flow(self):
        """Test that comando_torrents_flow can be imported."""
        from scrapers.comando_torrents import comando_torrents_flow

        assert callable(comando_torrents_flow)

    def test_all_attribute_exists(self):
        """Test that __all__ is defined in comando_torrents package."""
        from scrapers import comando_torrents

        assert hasattr(comando_torrents, "__all__")
        assert isinstance(comando_torrents.__all__, (list, tuple))
        assert len(comando_torrents.__all__) > 0
