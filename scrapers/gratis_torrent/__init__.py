"""GratisTorrent movie scraper module.

Main entry point for scraping movies from https://gratistorrent.com.

Features:
    - Automatic movie link discovery from the main page
    - Detailed metadata extraction (title, IMDB, year, quality, etc.)
    - Prefect orchestration with automatic retries
    - BigQuery integration for cloud storage
    - Data quality validation

Main exports:
    - scrape_all_movies: High-level scraping function
    - gratis_torrent_flow: Prefect orchestration flow
    - GratisTorrentConfig: Configuration settings
    - Movie: Data model
    - load_movies_to_bigquery: Cloud storage function
"""

from scrapers.gratis_torrent.bigquery_client import load_movies_to_bigquery
from scrapers.gratis_torrent.config import GratisTorrentConfig
from scrapers.gratis_torrent.flow import gratis_torrent_flow
from scrapers.gratis_torrent.http_client import collect_movie_links, fetch_page
from scrapers.gratis_torrent.models import Movie
from scrapers.gratis_torrent.parser import parse_movie_page
from scrapers.gratis_torrent.scraper import scrape_all_movies

__all__ = [
    # Main functions
    "scrape_all_movies",
    "gratis_torrent_flow",
    # Configuration
    "GratisTorrentConfig",
    # Models
    "Movie",
    # BigQuery
    "load_movies_to_bigquery",
    # HTTP Client
    "fetch_page",
    "collect_movie_links",
    # Parser
    "parse_movie_page",
]
