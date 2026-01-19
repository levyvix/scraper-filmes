"""Scraper-Filmes: Movie scraping system with dual scrapers.

A production-ready movie scraping system with two independent scrapers:
1. **GratisTorrent**: Full-featured scraper with BigQuery integration
2. **Comando Torrents**: Lightweight stealth scraper with Cloudflare bypass

Quick Start:
    from scrapers import scrape_gratis_torrent, GratisTorrentConfig

    config = GratisTorrentConfig()
    movies = scrape_gratis_torrent()

For advanced usage:
    from scrapers.gratis_torrent import gratis_torrent_flow
    result = gratis_torrent_flow()
"""

# High-level convenience exports
from scrapers.gratis_torrent import GratisTorrentConfig, Movie, gratis_torrent_flow
from scrapers.gratis_torrent import scrape_all_movies as scrape_gratis_torrent

# Utilities (shared across scrapers)
# Exception types
from scrapers.utils import (
    BigQueryException,
    DataQualityChecker,
    FetchException,
    ParsingException,
    ScraperException,
    ValidationException,
    parse_int,
    parse_rating,
    parse_year,
)

__all__ = [
    # Main GratisTorrent exports
    "scrape_gratis_torrent",
    "GratisTorrentConfig",
    "gratis_torrent_flow",
    "Movie",
    # Utilities
    "DataQualityChecker",
    "parse_rating",
    "parse_year",
    "parse_int",
    # Exceptions
    "ScraperException",
    "FetchException",
    "ParsingException",
    "ValidationException",
    "BigQueryException",
]
