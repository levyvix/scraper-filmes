# Change: Python Module Best Practices & TDD Coverage

## Why

Current codebase has 39% test coverage with critical infrastructure (BigQuery, Prefect flows) completely untested. Module organization follows ad-hoc patterns with empty `__init__.py` files, no public API, lazy imports inside functions, and hardcoded configuration values scattered across 8+ files. Sequential HTTP requests create performance bottlenecks (100s for 50 movies). These issues risk production failures, make the codebase difficult to maintain, and slow down development velocity.

## What Changes

### Module Organization (HIGH PRIORITY)
- Add proper `__init__.py` exports with `__all__` declarations (4 packages)
- Create `scrapers/utils/constants.py` for centralized configuration
- Standardize import patterns (move lazy imports to module top)
- Delete dead code (`monitoring.py` - 97 unused lines)

### Configuration Management (**BREAKING**)
- Replace global Config singleton with dependency injection
- Add factory functions: `get_config()` → `GratisTorrentConfig()`
- Move 10+ hardcoded values to constants (timeouts, retries, thresholds)
- Enhance Pydantic validation with `cached_property` for computed paths

### Resource Management (CRITICAL)
- **BREAKING**: Convert `bigquery_client.py` to context manager class
- Add cache cleanup context manager
- Ensure proper connection lifecycle and error handling

### Performance (**BREAKING**)
- Add async HTTP client with connection pooling (`async_http_client.py`)
- Add async scraper with concurrent requests (`async_scraper.py`)
- 10x performance improvement: 100s → 10s for 50 movies
- Requires new dependency: `httpx`

### Test Coverage (0% → 80%+)
- Fix Comando Torrents test failures (camoufox import error)
- Add BigQuery client tests (0% → 80%)
- Add Prefect flow execution tests (0% → 80%)
- Add integration tests for complete pipelines
- Add 114+ new test functions across 6 test files

## Impact

### Affected Specs
- **NEW**: `module-structure` - Public API design
- **NEW**: `configuration` - Config management patterns
- **NEW**: `resource-management` - Context managers
- **NEW**: `http-client` - Sync and async clients
- **NEW**: `testing` - TDD workflow and coverage
- **NEW**: `code-quality` - Import patterns, dead code

### Affected Code (Critical Files)
- `scrapers/__init__.py` - Add public API exports
- `scrapers/gratis_torrent/__init__.py` - Add exports
- `scrapers/comando_torrents/__init__.py` - Add exports
- `scrapers/utils/__init__.py` - Add exports
- `scrapers/utils/constants.py` - **NEW FILE** (centralized config)
- `scrapers/gratis_torrent/config.py` - Add factory, cached_property
- `scrapers/gratis_torrent/bigquery_client.py` - **BREAKING**: Context manager class
- `scrapers/gratis_torrent/async_http_client.py` - **NEW FILE** (async HTTP)
- `scrapers/gratis_torrent/async_scraper.py` - **NEW FILE** (concurrent scraping)
- `scrapers/gratis_torrent/scraper.py` - Dependency injection, constants
- `scrapers/gratis_torrent/flow.py` - Use new clients
- `scrapers/utils/monitoring.py` - **DELETE** (dead code)
- All test files - Add 114+ new tests

### Breaking Changes
1. **BigQuery API**: `load_movies_to_bigquery()` signature changes
   - Before: `load_movies_to_bigquery(movies: list[Movie])`
   - After: `load_movies_to_bigquery(movies: list[Movie], config: GratisTorrentConfig)`
   - Migration: Use context manager `with BigQueryClient(config) as bq: bq.load_movies(movies)`

2. **Config Singleton Removed**
   - Before: `from scrapers.gratis_torrent.config import Config` (global)
   - After: `from scrapers.gratis_torrent.config import get_config; config = get_config()`
   - Migration: Pass config explicitly or use factory

3. **Async Scraper** (Optional, new feature)
   - Add: `from scrapers.gratis_torrent import scrape_all_movies_async`
   - Requires: `uv add httpx`

### Dependencies Added
- `httpx` - Async HTTP client with HTTP/2 support

### Timeline Estimate
- Phase 0 (Emergency): 30 min
- Phase 1 (Quick Wins): 3.5 hours
- Phase 2 (BigQuery): 4 hours
- Phase 3 (Flows): 3 hours
- Phase 4 (Async): 5 hours
- Phase 5 (Polish): 2 hours
- **Total**: ~18 hours (2-3 days)

### Success Metrics
- **Before**: Coverage 39%, Empty `__init__.py`, 0 context managers, 100s scrape time
- **After**: Coverage 80%+, Public API, Context managers, 10s scrape time
