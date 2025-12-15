"""Configuration module for GratisTorrent scraper."""

import logging
import os
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class GratisTorrentConfig(BaseSettings):
    """Configuration settings with validation.

    Environment Variable Precedence:
        1. Environment variables (highest priority) - set at runtime or via Prefect job_variables
        2. .env file - loaded from .env in project root
        3. Default values (lowest priority) - hardcoded in this file

    Example for Prefect Deployment:
        In prefect.yaml, set job_variables:
            job_variables:
              GCP_PROJECT_ID: "your-project-id"
              GCP_CREDENTIALS_METHOD: "ADC"  # or "FILE"
              GCP_CREDENTIALS_PATH: "/path/to/service-account.json"  # if using FILE

    Example for Local Development:
        Create .env file:
            GCP_PROJECT_ID=your-project-id
            GCP_CREDENTIALS_METHOD=ADC

    Credential Methods:
        - ADC: Use Application Default Credentials (gcloud, workload identity, etc.)
        - FILE: Use service account JSON file (set GCP_CREDENTIALS_PATH)
    """

    # GCP Settings
    GCP_PROJECT_ID: str = Field(
        default="galvanic-flame-384620",
        description="Google Cloud Project ID. Loaded from env vars, .env, or default",
    )
    GCP_CREDENTIALS_METHOD: str = Field(
        default="ADC",
        description='Credential method: "ADC" (Application Default Credentials), "FILE" (service account JSON)',
    )
    GCP_CREDENTIALS_PATH: str | None = Field(
        default=None, description="Path to GCP service account JSON file (required if METHOD=FILE)"
    )
    DATASET_ID: str = Field(default="movies_raw", description="BigQuery dataset")
    TABLE_ID: str = Field(default="filmes", description="Main table name")
    STAGING_TABLE_ID: str = Field(default="stg_filmes", description="Staging table")
    LOCATION: str = Field(default="US", description="BigQuery location")

    # Scraper Settings
    BASE_URL: str = Field(
        default="https://gratistorrent.com/lancamentos/",
        description="Base URL for scraping",
    )
    REQUEST_TIMEOUT: int = Field(default=40, ge=1, le=300, description="Request timeout in seconds")

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
        if v in ("your-project-id", "YOUR_PROJECT_ID", "", "None", None):
            raise ValueError("GCP_PROJECT_ID must be set to a valid project ID")
        return v

    @field_validator("GCP_CREDENTIALS_METHOD")
    @classmethod
    def validate_credentials_method(cls, v: str) -> str:
        """Validate credential method is one of the supported options."""
        valid_methods = ("ADC", "FILE")
        if v not in valid_methods:
            raise ValueError(f"GCP_CREDENTIALS_METHOD must be one of {valid_methods}, got {v}")
        return v

    def __init__(self, **data):
        """Initialize config and log environment variable setup."""
        super().__init__(**data)
        # Log which source provided the values
        gcp_project_source = "env var" if os.environ.get("GCP_PROJECT_ID") else ".env or default"
        credentials_method_source = "env var" if os.environ.get("GCP_CREDENTIALS_METHOD") else "default"
        logger.info(
            f"GCP Configuration loaded: project_id from {gcp_project_source}, "
            f"credentials_method={self.GCP_CREDENTIALS_METHOD} from {credentials_method_source}"
        )

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
Config = GratisTorrentConfig()  # type: ignore
