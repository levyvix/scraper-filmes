# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Scraper-Filmes** is a production-ready movie scraping system with dual scrapers for different Brazilian torrent websites. The project features a full workflow orchestration pipeline with optional BigQuery export, comprehensive data validation, and intelligent caching strategies.

- **GratisTorrent Scraper**: Full-featured scraper with Prefect workflows and BigQuery integration
- **Comando Torrents Scraper**: Lightweight stealth scraper with Cloudflare bypass and local JSON output
- **Data Validation**: Pydantic models with field-level validation (IMDB range, year >= 1888, etc.)
- **Workflow Orchestration**: Prefect-based pipelines with automatic retries and error handling
- **Cloud Integration**: Optional Google BigQuery export with staging tables and merge deduplication

## Development Environment

### Prerequisites
- Python 3.11+
- UV for dependency management (see `.claude/CLAUDE.md` for conventions)

### Setup
```bash
uv sync
cp .env.example .env  # Edit with GCP_PROJECT_ID if using BigQuery
```

## Common Commands

### Development
```bash
# Run main GratisTorrent scraper
uv run run_gratis.py

# Run Comando Torrents scraper (lightweight, local output)
uv run run_comando.py

# Run specific test file
uv run pytest scrapers -v

# Linting and formatting (with 120 char line length)
uvx ruff check --fix . && uvx ruff format --line-length 120

# Type checking
uvx mypy --ignore-missing-imports .
```

## Architecture and Data Flow

### Layered Architecture

```
HTTP Client (fetch_page)
    ↓
Parser (parse_movie_page, extract_regex_field, etc.)
    ↓
Shared Utils (parse_utils.py - parse_rating, parse_year, parse_int)
    ↓
Models (Pydantic validation - Movie class from utils/models.py)
    ↓
Scraper (orchestration, DiskCache memoization)
    ↓
Prefect Flow (task coordination with retries)
    ↓
BigQuery Client (staging → merge → dedup)
    ↓
Cloud Storage (movies_raw.filmes dataset)
```


### Key Components

1. **Shared Utils** (`scrapers/utils/`)
   - `parse_utils.py`: Reusable parsing functions
     - `parse_rating()`: Convert rating text to float (handles comma/dot)
     - `parse_year()`: Convert year text to int with validation
     - `parse_int()`: Generic integer parser with error handling
   - `models.py`: Base Movie model (Pydantic BaseModel)
     - Shared across both scrapers for consistency
     - Field validations: IMDB (0-10), year (≥1888)
   - `send_mail.py`: Email notification utility

2. **Data Models** (`scrapers/gratis_torrent/models.py`)
   - Extends base `Movie` from `scrapers/utils/models.py`
   - Additional scraper-specific fields if needed
   - All fields nullable by design for partial data

3. **Parser** (`scrapers/gratis_torrent/parser.py`)
   - Regex-based field extraction (12 patterns)
   - Uses shared utils for type conversions
   - Functions: `extract_movie_fields()`, `parse_movie_page()`, `clean_genre()`, etc.
   - Handles partial failures gracefully

4. **HTTP Client** (`scrapers/gratis_torrent/http_client.py`)
   - `fetch_page()`: BeautifulSoup wrapper with 40s timeout
   - `collect_movie_links()`: CSS selector `#capas_pequenas > div > a`
   - Link deduplication while preserving order

5. **Scraper** (`scrapers/gratis_torrent/scraper.py`)
   - Entry point: `scrape_all_movies()`
   - Uses DiskCache (1-hour TTL) in `./movie_cache/`
   - Returns list of movie dictionaries
   - Logs progress to console

6. **Prefect Workflow** (`scrapers/gratis_torrent/flow.py`)
   - Task 1: `scrape-movies` (2 retries, 30s delay)
   - Task 2: `load-to-bigquery` (3 retries, 60s delay)
   - Output: `{"movies_scraped": N, "rows_loaded": M}`

7. **BigQuery Integration** (`scrapers/gratis_torrent/bigquery_client.py`)
   - Setup: Creates dataset and tables if missing
   - Pipeline: Load to staging → MERGE to main (dedup on `link` field) → truncate staging
   - Handles schema from `schema.json`
   - Returns row count of merged/inserted records

8. **Configuration** (`scrapers/gratis_torrent/config.py`)

   - Dataset: `movies_raw` (us-central)
   - Tables: `filmes` (main), `stg_filmes` (staging)
   - Base URL: `https://gratistorrent.com/lancamentos/`
   - Timeout: 40 seconds

### Caching Strategy

- **DiskCache**: `./movie_cache/` with 1-hour expiry
- **Memoization**: Applied to `scrape_all_movies()` function
- **Result**: Prevents redundant scraping within TTL window
- **Location specific**: Each scraper has own cache directory

### Error Handling

- **HTTP failures**: Logged, returns None, continues processing
- **Parse failures**: Movie skipped, warning logged
- **Validation errors**: Movie rejected, error logged (Pydantic catches)
- **BigQuery failures**: Prefect retries with exponential backoff (2-3 attempts)

## Testing

### Custom Test Suite
Located in `tests/test_suite.py` with 8 comprehensive tests:
1. Module imports verification
2. Pydantic model validation (valid/invalid data)
3. Configuration parsing
4. Parser functions (regex, type conversion)
5. Model serialization
6. Prefect flow structure
7. HTTP client functions
8. BigQuery schema validation

### Pytest Unit Tests
Located in `tests/scrapers/gratis_torrent/`:
- `test_models.py`: Movie model instantiation and validation
- `test_parser.py`: Parser function correctness
- `test_config.py`: Configuration loading
- `test_http_client.py`: HTTP client behavior

### Running Tests
```bash
# All tests
uv run pytest scrapers/

# With coverage
uv run pytest scrapers/ --cov=scrapers --cov-report=term-missing
```

## Configuration and Environment

### Environment Variables
```bash
GCP_PROJECT_ID=your-gcp-project-id  # Required for BigQuery
```

### Project Structure
- **Config precedence**: .env → hardcoded defaults (config.py) → Prefect parameters
- **BigQuery schema**: `scrapers/gratis_torrent/schema.json`
- **Prefect config**: `prefect.yaml` (hourly schedule)
- **Docker**: Minimal Dockerfile for containerization

## Deployment

### Local Execution
```bash
uv run main.py
```

### Prefect Deployment
See `docs/PREFECT_DEPLOYMENT.md` for:
- Flow setup and scheduling
- Prefect Cloud integration
- Work pool configuration

### BigQuery Setup
See `docs/BIGQUERY_SETUP.md` for:
- GCP project setup
- Service account configuration
- Dataset/table creation
- Authentication methods

## Dual Scraper Strategy

### GratisTorrent (Production-Grade)
- Full workflow with retries and monitoring
- BigQuery integration for centralized data
- Prefect orchestration with scheduling
- Uses shared utils for parsing and validation
- Use for: Regular, reliable data collection

### Comando Torrents (Lightweight)
- Standalone Python script
- Stealth scraping with Scrapling (Cloudflare bypass)
- Local JSON output (`movies.json`)
- DiskCache for optimization
- Uses shared utils for parsing and validation
- Use for: Quick scraping, specific site, no infrastructure

Both share: Pydantic validation from `scrapers/utils/models.py`, parsing utilities from `scrapers/utils/parse_utils.py`, similar data models, error handling patterns


## Incremental Development Notes

### When Adding New Fields to Movies
1. Update `Movie` model in `scrapers/utils/models.py` (add field and validation if needed)
2. Add regex pattern in scraper-specific `parser.py` `extract_movie_fields()`
3. Update BigQuery schema in `schema.json` (if using GratisTorrent scraper)
4. Update tests in `test_models.py` and `test_parser.py`
5. Run full test suite: `uv run pytest scrapers/`

### When Modifying Parsing Logic
- Parser functions in `parser.py` are independent; test them in isolation
- Use shared utils from `scrapers/utils/parse_utils.py` for common parsing tasks
- Use `create_movie_object()` for end-to-end validation
- Regex patterns should include named groups for clarity
- Add test cases for edge cases (missing fields, malformed data)

### When Changing BigQuery Schema
1. Update `schema.json` (field names and types)
2. Update `Movie` model in `scrapers/utils/models.py` to match schema
3. Run the scraper to verify connectivity: `uv run run_gratis.py`

4. First MERGE will create new schema version (tables are idempotent)

## Performance Considerations

- **Current bottleneck**: Sequential HTTP requests (no async/await)
- **Cache hit rate**: Depends on scrape frequency vs. 1-hour TTL
- **Prefect tasks**: Simple retries, not distributed; scale via Prefect Cloud
- **BigQuery**: Staging table ensures transactional safety; MERGE is atomic