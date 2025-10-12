# GratisTorrent Scraper

A modular, well-tested movie scraper for GratisTorrent with BigQuery integration and Prefect orchestration.

## Architecture

The scraper follows Python best practices with clear separation of concerns:

```
src/scrapers/gratis_torrent/
├── config.py          # Configuration and constants
├── models.py          # Pydantic data models
├── http_client.py     # HTTP fetching and page loading
├── parser.py          # HTML parsing and data extraction (pure functions)
├── scraper.py         # Orchestration of scraping logic
├── bigquery_client.py # BigQuery operations
└── flow.py            # Prefect flow definition
```

## Modules

### `config.py`
Centralized configuration management:
- GCP project settings
- Table and dataset IDs
- Scraper settings (URL, timeout)
- File paths

### `models.py`
Pydantic models for data validation:
- `Movie`: Validated movie data model with field constraints

### `http_client.py`
HTTP operations:
- `fetch_page()`: Fetch and parse HTML pages with BeautifulSoup
- `collect_movie_links()`: Extract movie URLs from listing pages

### `parser.py`
Pure parsing functions (easily testable):
- `extract_regex_field()`: Extract single field with regex
- `safe_convert_float()`, `safe_convert_int()`: Safe type conversions
- `extract_sinopse()`: Extract movie synopsis
- `extract_movie_fields()`: Extract all movie metadata
- `clean_genre()`: Clean genre formatting
- `create_movie_object()`: Create and validate Movie objects
- `parse_movie_page()`: Main parsing orchestration

### `scraper.py`
High-level scraping orchestration:
- `scrape_movie_links()`: Get all movie URLs from main page
- `scrape_movie_details()`: Scrape single movie details
- `scrape_all_movies()`: Complete scraping pipeline

### `bigquery_client.py`
BigQuery operations:
- `get_client()`: Create BigQuery client
- `load_schema()`: Load table schema from JSON
- `create_dataset()`, `create_table()`: Setup infrastructure
- `load_data_to_staging()`: Load data to staging table
- `merge_staging_to_main()`: Merge with deduplication
- `truncate_staging_table()`: Clean up staging
- `load_movies_to_bigquery()`: Complete load pipeline

### `flow.py`
Prefect flow (no data processing):
- `scrape_movies_task()`: Scraping task with retries
- `load_to_bigquery_task()`: Loading task with retries
- `gratis_torrent_flow()`: Main flow orchestration

## Usage

### Run the Prefect Flow

```bash
uv run python -m src.scrapers.gratis_torrent.flow
```

### Use Individual Components

```python
from src.scrapers.gratis_torrent import (
    scrape_all_movies,
    load_movies_to_bigquery,
    gratis_torrent_flow
)

# Scrape movies
movies = scrape_all_movies()

# Load to BigQuery
rows_affected = load_movies_to_bigquery(movies)

# Or run complete flow
result = gratis_torrent_flow()
```

## Testing

Run all tests:

```bash
uv run python -m pytest tests/scrapers/gratis_torrent/ -v
```

Run specific test file:

```bash
uv run python -m pytest tests/scrapers/gratis_torrent/test_parser.py -v
```

### Test Coverage

- **49 unit tests** covering all modules
- Parser functions (pure functions, easily testable)
- HTTP client operations (with mocks)
- Data models and validation
- Configuration management

## Development

### Code Quality

Format code:
```bash
uvx ruff format --line-length 120 src/scrapers/gratis_torrent/
```

Lint code:
```bash
uvx ruff check src/scrapers/gratis_torrent/
```

Auto-fix linting issues:
```bash
uvx ruff check --fix src/scrapers/gratis_torrent/
```

## Design Principles

1. **Modularity**: Each module has a single, well-defined responsibility
2. **Testability**: Pure functions in parser.py make testing straightforward
3. **Type Safety**: Pydantic models ensure data validation
4. **Configuration**: Centralized config management
5. **Error Handling**: Graceful error handling with logging
6. **Separation of Concerns**: Prefect flow only orchestrates, doesn't process data
7. **Python Best Practices**: Type hints, docstrings, clear naming

## Environment Variables

Create a `.env` file in the project root:

```env
GCP_PROJECT_ID=your-project-id
```

## Dependencies

Managed via `uv`:
- `requests`: HTTP client
- `beautifulsoup4`: HTML parsing
- `pydantic`: Data validation
- `loguru`: Logging
- `google-cloud-bigquery`: BigQuery client
- `prefect`: Workflow orchestration
- `python-dotenv`: Environment variable management
