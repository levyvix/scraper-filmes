"""Comando Torrents movie scraper module.

Lightweight stealth scraper for https://comandotorrents.fun.

Features:
    - Cloudflare bypass using Scrapling library
    - Stealth browser automation with browser fingerprinting
    - Quality validation
    - Local JSON output

Main exports:
    - comando_torrents_flow: Prefect orchestration flow
    - ComandoTorrentsConfig: Configuration settings
    - get_movie_links: Extract movie links from website
"""

from scrapers.comando_torrents.config import ComandoTorrentsConfig
from scrapers.comando_torrents.flow import comando_torrents_flow
from scrapers.comando_torrents.scraper import get_movie_links

__all__ = [
    # Main functions
    "comando_torrents_flow",
    "get_movie_links",
    # Configuration
    "ComandoTorrentsConfig",
]
