"""Configuration module for GratisTorrent scraper."""

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class GratisTorrentConfig(BaseSettings):
    """Configuration settings with validation."""

    # GCP Settings
    GCP_PROJECT_ID: str = Field(..., description="Google Cloud Project ID")
    DATASET_ID: str = Field(default="movies_raw", description="BigQuery dataset")
    TABLE_ID: str = Field(default="filmes", description="Main table name")
    STAGING_TABLE_ID: str = Field(default="stg_filmes", description="Staging table")
    LOCATION: str = Field(default="US", description="BigQuery location")

    # Scraper Settings
    BASE_URL: str = Field(
        default="https://gratistorrent.com/lancamentos/",
        description="Base URL for scraping",
    )
    REQUEST_TIMEOUT: int = Field(
        default=40, ge=1, le=300, description="Request timeout in seconds"
    )

    # Email Settings (optional)
    EMAIL: str | None = Field(default=None, description="Email for notifications")
    EMAIL_PW: str | None = Field(default=None, description="Email password")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("GCP_PROJECT_ID")
    @classmethod
    def validate_project_id(cls, v: str) -> str:
        """Validate that GCP_PROJECT_ID is set to a valid value."""
        if not v or v in ("your-project-id", "YOUR_PROJECT_ID", ""):
            raise ValueError(
                "GCP_PROJECT_ID must be set to a valid project ID in .env file"
            )
        return v

    # File Paths (computed properties)
    @property
    def PROJECT_ROOT(self) -> Path:
        """Get project root directory."""
        return Path(__file__).parent

    @property
    def SCHEMA_FILE(self) -> Path:
        """Get schema file path."""
        return self.PROJECT_ROOT / "schema.json"

    @property
    def MOVIES_JSON_PATH(self) -> Path:
        """Get movies JSON file path."""
        return self.PROJECT_ROOT / "movies.jsonl"

    def get_full_table_id(self, table_name: str) -> str:
        """Get fully qualified table ID."""
        return f"{self.GCP_PROJECT_ID}.{self.DATASET_ID}.{table_name}"


# Singleton instance for backward compatibility
Config = GratisTorrentConfig()
