"""Tests for config module."""

from pathlib import Path

from src.scrapers.gratis_torrent.config import Config


class TestConfig:
    """Tests for Config class."""

    def test_default_values(self):
        """Test that default configuration values are set."""
        assert Config.GCP_PROJECT_ID is not None
        assert Config.DATASET_ID == "movies_raw"
        assert Config.TABLE_ID == "filmes"
        assert Config.STAGING_TABLE_ID == "stg_filmes"
        assert Config.LOCATION == "US"
        assert Config.BASE_URL == "https://gratistorrent.com/lancamentos/"
        assert Config.REQUEST_TIMEOUT == 40

    def test_paths_are_path_objects(self):
        """Test that file paths are Path objects."""
        assert isinstance(Config.PROJECT_ROOT, Path)
        assert isinstance(Config.SCHEMA_FILE, Path)

    def test_get_full_table_id(self):
        """Test constructing full table ID."""
        table_id = Config.get_full_table_id("test_table")
        expected = f"{Config.GCP_PROJECT_ID}.{Config.DATASET_ID}.test_table"
        assert table_id == expected

    def test_get_full_table_id_main_table(self):
        """Test constructing full table ID for main table."""
        table_id = Config.get_full_table_id(Config.TABLE_ID)
        assert table_id.endswith(".movies_raw.filmes")

    def test_get_full_table_id_staging_table(self):
        """Test constructing full table ID for staging table."""
        table_id = Config.get_full_table_id(Config.STAGING_TABLE_ID)
        assert table_id.endswith(".movies_raw.stg_filmes")
