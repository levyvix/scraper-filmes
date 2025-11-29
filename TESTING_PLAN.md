# Testing Plan for Scrapers

This document outlines the plan to achieve at least 80% test coverage for `scrapers/comando_torrents` and `scrapers/gratis_torrents`.

## Phase 1: Setup and Dependencies

1.  **Install Testing Dependencies**: Use `uv add pytest pytest-cov` to install `pytest` for running tests and `pytest-cov` for coverage reporting.

## Phase 2: Testing `scrapers/comando_torrents`

1.  **Create Test File**: Create a new file `tests/scrapers/comando_torrents/test_main.py`.
2.  **Mock External Dependencies**: Mock external dependencies such as `StealthySession`, `Adaptor`, `Cache`, and `Config` to ensure that unit tests are isolated and do not make actual network requests or rely on cached data.
3.  **Write Unit Tests**: Write comprehensive unit tests for the following functions in `src/scrapers/comando_torrents/main.py`:
    *   `fetch_page_html`: Test successful fetching and error handling.
    *   `fetch_page`: Test successful page retrieval and cases where `fetch_page_html` returns `None`.
    *   `extract_text_or_none`: Test extraction of text, empty results, and missing selectors.
    *   `safe_list_get`: Test valid index access and out-of-range scenarios.
    *   `parse_detail`: Test successful parsing of movie details, handling of missing/incomplete data, and `ValidationError` cases. This will involve mocking the `fetch_page` and `extract_text_or_none` calls.
    *   `get_movie_links`: Test successful link extraction and error handling.
    *   `main`: Test the overall flow, ensuring it calls other functions correctly and handles various scenarios (e.g., no links found, no movies scraped). This will require extensive mocking.
    *   `save_to_json`: Test that movie data is correctly serialized and written to a JSON file.

## Phase 3: Testing `scrapers/gratis_torrents`

1.  **Create Test File**: Create a new file `tests/scrapers/gratis_torrent/test_scraper.py`.
2.  **Mock External Dependencies**: Mock dependencies like `fetch_page`, `collect_movie_links`, `parse_movie_page`, `Config`, and `Cache` to ensure isolated unit tests.
3.  **Write Unit Tests**: Write comprehensive unit tests for the following functions in `src/scrapers/gratis_torrent/scraper.py`:
    *   `scrape_movie_links`: Test successful link collection and error handling when `fetch_page` fails.
    *   `scrape_movie_details`: Test successful detail scraping and cases where `fetch_page` or `parse_movie_page` fail.
    *   `scrape_all_movies`: Test the orchestration of scraping multiple movies, including scenarios where some movie details fail to scrape.

## Phase 4: Coverage and Refinement

1.  **Run Tests and Check Coverage**: After writing the initial tests, run them using `pytest --cov=src/scrapers/comando_torrents --cov=src/scrapers/gratis_torrent tests/scrapers/comando_torrents tests/scrapers/gratis_torrent`.
2.  **Achieve 80% Coverage**: Analyze the coverage report and add additional tests or refine existing ones to ensure that both `src/scrapers/comando_torrents/main.py` and `src/scrapers/gratis_torrent/scraper.py` achieve at least 80% line coverage.
