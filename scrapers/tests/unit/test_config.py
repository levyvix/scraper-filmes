import os

import pytest

from scrapers.gratis_torrent.config import Config, GratisTorrentConfig


def test_config_properties():
    """Tests the essential properties of the Config class."""
    assert Config.GCP_PROJECT_ID == "galvanic-flame-384620"
    assert Config.DATASET_ID == "movies_raw"
    assert Config.TABLE_ID == "filmes"
    assert Config.LOCATION == "US"
    assert Config.GCP_CREDENTIALS_METHOD in ("ADC", "FILE")


def test_config_credentials_method_validation():
    """Tests that invalid credential methods are rejected."""
    with pytest.raises(ValueError, match="GCP_CREDENTIALS_METHOD must be one of"):
        GratisTorrentConfig(GCP_CREDENTIALS_METHOD="INVALID")


def test_config_env_var_override():
    """Tests that environment variables override config defaults."""
    original_method = os.environ.get("GCP_CREDENTIALS_METHOD")
    try:
        os.environ["GCP_CREDENTIALS_METHOD"] = "FILE"
        config = GratisTorrentConfig()
        assert config.GCP_CREDENTIALS_METHOD == "FILE"
    finally:
        if original_method:
            os.environ["GCP_CREDENTIALS_METHOD"] = original_method
        else:
            os.environ.pop("GCP_CREDENTIALS_METHOD", None)


def test_config_methods():
    """Tests the helper methods of the Config class."""
    full_table_id = Config.get_full_table_id(Config.TABLE_ID)
    project = Config.GCP_PROJECT_ID
    dataset = Config.DATASET_ID
    table = Config.TABLE_ID
    expected_id = f"{project}.{dataset}.{table}"
    assert full_table_id == expected_id
