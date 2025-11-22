from scrapers.gratis_torrent.config import Config


def test_config_properties():
    """Tests the essential properties of the Config class."""
    assert Config.GCP_PROJECT_ID is not None
    assert Config.DATASET_ID == "movies_raw"
    assert Config.TABLE_ID == "filmes"
    assert Config.LOCATION == "US"


def test_config_methods():
    """Tests the helper methods of the Config class."""
    full_table_id = Config.get_full_table_id(Config.TABLE_ID)
    project = Config.GCP_PROJECT_ID
    dataset = Config.DATASET_ID
    table = Config.TABLE_ID
    expected_id = f"{project}.{dataset}.{table}"
    assert full_table_id == expected_id
