"""Tests for config factory functions.

Verifies that configuration can be instantiated via factory functions
and that each factory call returns a fresh instance (not a singleton).
"""

from pathlib import Path
from unittest.mock import patch


class TestGratisTorrentConfigFactory:
    """Test get_config factory function for GratisTorrentConfig."""

    def test_get_config_returns_instance(self):
        """Test that get_config returns a GratisTorrentConfig instance."""
        from scrapers.gratis_torrent.config import get_config

        config = get_config()
        assert config is not None

    def test_get_config_returns_different_instances(self):
        """Test that multiple calls to get_config return different instances (not singleton)."""
        from scrapers.gratis_torrent.config import get_config

        config1 = get_config()
        config2 = get_config()

        # Should be different instances (not singleton)
        assert config1 is not config2

    def test_get_config_uses_env_file(self):
        """Test that get_config loads from .env file."""
        from scrapers.gratis_torrent.config import get_config

        with patch.dict("os.environ", {"GCP_PROJECT_ID": "test-project"}):
            config = get_config()
            assert config.GCP_PROJECT_ID == "test-project"

    def test_get_config_has_required_fields(self):
        """Test that returned config has all required fields."""
        from scrapers.gratis_torrent.config import get_config

        config = get_config()
        assert hasattr(config, "GCP_PROJECT_ID")
        assert hasattr(config, "DATASET_ID")
        assert hasattr(config, "TABLE_ID")
        assert hasattr(config, "BASE_URL")
        assert hasattr(config, "REQUEST_TIMEOUT")


class TestConfigCachedProperties:
    """Test cached_property decorators on config classes."""

    def test_config_schema_file_property(self):
        """Test that SCHEMA_FILE is a computed property."""
        from scrapers.gratis_torrent.config import get_config

        config = get_config()
        schema_file = config.SCHEMA_FILE

        assert isinstance(schema_file, Path)
        assert schema_file.name == "schema.json"

    def test_config_movies_json_path_property(self):
        """Test that MOVIES_JSON_PATH is a computed property."""
        from scrapers.gratis_torrent.config import get_config

        config = get_config()
        json_path = config.MOVIES_JSON_PATH

        assert isinstance(json_path, Path)
        assert json_path.name == "movies.jsonl"

    def test_config_project_root_property(self):
        """Test that PROJECT_ROOT is a computed property."""
        from scrapers.gratis_torrent.config import get_config

        config = get_config()
        project_root = config.PROJECT_ROOT

        assert isinstance(project_root, Path)
        assert project_root.exists()

    def test_cached_properties_are_consistent(self):
        """Test that repeated access to cached properties returns same value."""
        from scrapers.gratis_torrent.config import get_config

        config = get_config()

        # Call twice and verify same result
        path1 = config.SCHEMA_FILE
        path2 = config.SCHEMA_FILE

        assert path1 == path2


class TestComandoTorrentsConfig:
    """Test configuration for Comando Torrents scraper."""

    def test_comando_config_exists(self):
        """Test that ComandoTorrentsConfig can be imported."""
        from scrapers.comando_torrents.config import ComandoTorrentsConfig

        assert ComandoTorrentsConfig is not None

    def test_comando_config_has_required_fields(self):
        """Test that ComandoTorrentsConfig has required fields."""
        from scrapers.comando_torrents.config import ComandoTorrentsConfig

        config = ComandoTorrentsConfig()
        assert hasattr(config, "URL_BASE")
        assert config.URL_BASE is not None
        assert len(config.URL_BASE) > 0
        assert hasattr(config, "JSON_FILE_NAME")
        assert config.JSON_FILE_NAME is not None
