"""Configuration module for Comando Torrents scraper."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ComandoTorrentsConfig(BaseSettings):
    """Configuration settings for Comando Torrents scraper."""

    URL_BASE: str = Field(
        default="https://comando.la/category/filmes/",
        description="Base URL for scraping",
    )
    JSON_FILE_NAME: str = Field(
        default="movies.json",
        description="Output JSON file name",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# Singleton instance for backward compatibility
Config = ComandoTorrentsConfig()

