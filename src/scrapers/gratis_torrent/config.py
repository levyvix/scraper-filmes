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
    DATASET_ID: str = "movies_raw"
    TABLE_ID: str = "filmes"
    STAGING_TABLE_ID: str = "stg_filmes"
    LOCATION: str = "US"

    # Scraper Settings
    BASE_URL: str = "https://gratistorrent.com/lancamentos/"
    REQUEST_TIMEOUT: int = 40

    # File Paths
    PROJECT_ROOT: Path = Path(__file__).parent
    SCHEMA_FILE: Path = PROJECT_ROOT / "schema.json"

    @classmethod
    def get_full_table_id(cls, table_name: str) -> str:
        """Get fully qualified table ID."""
        return f"{cls.GCP_PROJECT_ID}.{cls.DATASET_ID}.{table_name}"
