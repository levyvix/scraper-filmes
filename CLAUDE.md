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
uv run main.py

# Run Comando Torrents scraper (lightweight, local output)
uv run src/scrapers/comando_torrents/main.py

# Run all tests (custom suite + pytest)
uv run tests/test_suite.py && uvx pytest tests/

# Run specific test file
uvx pytest tests/scrapers/gratis_torrent/test_parser.py -v

# Test BigQuery connectivity
uv run scripts/test_bigquery.py

# Linting and formatting (with 120 char line length)
uvx ruff check . && uvx ruff format --line-length 120

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
Models (Pydantic validation - Movie class)
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

1. **Data Models** (`src/scrapers/gratis_torrent/models.py`)
   - `Movie`: Pydantic BaseModel with 12 fields
   - Field validations: IMDB (0-10), year (≥1888), duration (≥1 min)
   - All fields nullable by design for partial data

2. **Parser** (`src/scrapers/gratis_torrent/parser.py`)
   - Regex-based field extraction (12 patterns)
   - Safe type conversions (float, int) with fallbacks
   - Functions: `extract_movie_fields()`, `parse_movie_page()`, `clean_genre()`, etc.
   - Handles partial failures gracefully

3. **HTTP Client** (`src/scrapers/gratis_torrent/http_client.py`)
   - `fetch_page()`: BeautifulSoup wrapper with 40s timeout
   - `collect_movie_links()`: CSS selector `#capas_pequenas > div > a`
   - Link deduplication while preserving order

4. **Scraper** (`src/scrapers/gratis_torrent/scraper.py`)
   - Entry point: `scrape_all_movies()`
   - Uses DiskCache (1-hour TTL) in `./movie_cache/`
   - Returns list of movie dictionaries
   - Logs progress to console

5. **Prefect Workflow** (`src/scrapers/gratis_torrent/flow.py`)
   - Task 1: `scrape-movies` (2 retries, 30s delay)
   - Task 2: `load-to-bigquery` (3 retries, 60s delay)
   - Output: `{"movies_scraped": N, "rows_loaded": M}`

6. **BigQuery Integration** (`src/scrapers/gratis_torrent/bigquery_client.py`)
   - Setup: Creates dataset and tables if missing
   - Pipeline: Load to staging → MERGE to main (dedup on `link` field) → truncate staging
   - Handles schema from `schema.json`
   - Returns row count of merged/inserted records

7. **Configuration** (`src/scrapers/gratis_torrent/config.py`)
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
uv run tests/test_suite.py && uvx pytest tests/

# Specific test file
uvx pytest tests/scrapers/gratis_torrent/test_models.py -v

# With coverage
uvx pytest tests/ --cov=src/scrapers --cov-report=term-missing
```

## Configuration and Environment

### Environment Variables
```bash
GCP_PROJECT_ID=your-gcp-project-id  # Required for BigQuery
```

### Project Structure
- **Config precedence**: .env → hardcoded defaults (config.py) → Prefect parameters
- **BigQuery schema**: `src/scrapers/gratis_torrent/schema.json`
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
- Use for: Regular, reliable data collection

### Comando Torrents (Lightweight)
- Standalone Python script
- Stealth scraping with Scrapling (Cloudflare bypass)
- Local JSON output (`movies.json`)
- DiskCache for optimization
- Use for: Quick scraping, specific site, no infrastructure

Both share: Pydantic validation, similar data models, error handling patterns

## Incremental Development Notes

### When Adding New Fields to Movies
1. Update `Movie` model in `models.py` (add field and validation if needed)
2. Add regex pattern in `parser.py` `extract_movie_fields()`
3. Update BigQuery schema in `schema.json`
4. Update tests in `test_models.py` and `test_parser.py`
5. Run full test suite: `uv run tests/test_suite.py && uvx pytest tests/`

### When Modifying Parsing Logic
- Parser functions in `parser.py` are independent; test them in isolation
- Use `create_movie_object()` for end-to-end validation
- Regex patterns should include named groups for clarity
- Add test cases for edge cases (missing fields, malformed data)

### When Changing BigQuery Schema
1. Update `schema.json` (field names and types)
2. Update `Movie` model to match schema
3. Run `scripts/test_bigquery.py` to verify connectivity
4. First MERGE will create new schema version (tables are idempotent)

## Performance Considerations

- **Current bottleneck**: Sequential HTTP requests (no async/await)
- **Cache hit rate**: Depends on scrape frequency vs. 1-hour TTL
- **Prefect tasks**: Simple retries, not distributed; scale via Prefect Cloud
- **BigQuery**: Staging table ensures transactional safety; MERGE is atomic

## Useful References

- Data Models: `src/scrapers/gratis_torrent/models.py:1-50`
- Parser entry point: `src/scrapers/gratis_torrent/parser.py:parse_movie_page()`
- Scraper entry point: `src/scrapers/gratis_torrent/scraper.py:scrape_all_movies()`
- Flow definition: `src/scrapers/gratis_torrent/flow.py:gratis_torrent_flow()`
- BigQuery pipeline: `src/scrapers/gratis_torrent/bigquery_client.py:load_movies_to_bigquery()`