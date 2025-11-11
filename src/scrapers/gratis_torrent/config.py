"""Configuration module for GratisTorrent scraper."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration settings for the scraper."""

    # GCP Settings
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "galvanic-flame-384620")
    # Dataset where raw data is stored
    DATASET_ID: str = "movies_raw"
    # Table where raw data is stored
    TABLE_ID: str = "filmes"
    # Table where staging data is stored
    STAGING_TABLE_ID: str = "stg_filmes"
    # BigQuery table location
    LOCATION: str = "US"

    # Scraper Settings
    BASE_URL: str = "https://gratistorrent.com/lancamentos/"
    REQUEST_TIMEOUT: int = 40

    # File Paths
    PROJECT_ROOT: Path = Path(__file__).parent
    SCHEMA_FILE: Path = PROJECT_ROOT / "schema.json"
    MOVIES_JSON_PATH: Path = PROJECT_ROOT / "movies.jsonl"

    @classmethod
    def get_full_table_id(cls, table_name: str) -> str:
        """Get fully qualified table ID."""
        return f"{cls.GCP_PROJECT_ID}.{cls.DATASET_ID}.{table_name}"
