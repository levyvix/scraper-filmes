# Implementation Tasks

## Phase 0: Emergency Fix (30 min)

- [ ] 0.1 Fix Comando Torrents test imports
  - [ ] Add pytest fixture to mock Scrapling/camoufox at import time
  - [ ] Update `scrapers/tests/conftest.py` with session-scoped mock
  - [ ] Verify: `uv run pytest scrapers/tests/unit/test_comando_scraper.py -v`

## Phase 1: Quick Wins - Module Organization (3.5 hours)

### 1.1 Create Constants Module (45 min)
- [ ] Create `scrapers/utils/constants.py`
- [ ] Extract 15+ hardcoded values with type hints and docstrings
- [ ] Write tests: `test_constants.py` (10 tests for import and values)

### 1.2 Add Public API Exports (90 min)
- [ ] Write tests FIRST for importability (RED)
  - [ ] `test_root_api.py` - Test `from scrapers import scrape_gratis_torrent`
  - [ ] `test_utils_api.py` - Test utils exports
  - [ ] `test_gratis_api.py` - Test gratis_torrent exports
  - [ ] `test_comando_api.py` - Test comando_torrents exports
- [ ] Implement `__init__.py` files with `__all__` (GREEN)
  - [ ] `scrapers/__init__.py` - 15+ exports
  - [ ] `scrapers/utils/__init__.py` - 12+ exports
  - [ ] `scrapers/gratis_torrent/__init__.py` - 6+ exports
  - [ ] `scrapers/comando_torrents/__init__.py` - 4+ exports
- [ ] Verify all tests pass (REFACTOR)

### 1.3 Standardize Imports (30 min)
- [ ] Move lazy imports from functions to module top
- [ ] Fix 25+ occurrences in:
  - [ ] `scrapers/gratis_torrent/scraper.py`
  - [ ] `scrapers/gratis_torrent/http_client.py`
  - [ ] `scrapers/comando_torrents/scraper.py`
- [ ] Run type checker: `uvx mypy --ignore-missing-imports .`

### 1.4 Delete Dead Code (15 min)
- [ ] Remove `scrapers/utils/monitoring.py` (97 lines)
- [ ] Verify no imports exist: `rg "from.*monitoring import" scrapers/`
- [ ] Run full test suite: `uv run pytest scrapers/ -v`

## Phase 2: Configuration Management (2 hours)

### 2.1 Update Config Classes (60 min)
- [ ] Write config tests FIRST (RED)
  - [ ] `test_config_factory.py` - Test `get_config()` returns new instance
  - [ ] `test_config_constants.py` - Test constants imported correctly
  - [ ] `test_config_validation.py` - Test Pydantic validators
- [ ] Update `scrapers/gratis_torrent/config.py` (GREEN)
  - [ ] Import constants from `utils.constants`
  - [ ] Add `@cached_property` for computed paths
  - [ ] Add `get_config()` factory function
  - [ ] Remove global singleton instance
- [ ] Update `scrapers/comando_torrents/config.py`
- [ ] Update all usages to use factory pattern (REFACTOR)

### 2.2 Replace Hardcoded Values (60 min)
- [ ] Update files to use constants:
  - [ ] `scrapers/gratis_torrent/scraper.py` - retry config, quality threshold
  - [ ] `scrapers/gratis_torrent/flow.py` - retry delays
  - [ ] `scrapers/gratis_torrent/bigquery_client.py` - timeout values
  - [ ] `scrapers/comando_torrents/flow.py` - quality threshold
- [ ] Run integration test: `uv run run_gratis.py` (dry run if possible)

## Phase 3: Resource Management (4 hours)

### 3.1 BigQuery Context Manager (2.5 hours)
- [ ] Write context manager tests FIRST (RED)
  - [ ] `test_bigquery_context_manager.py`:
    - [ ] Test `__enter__` creates client
    - [ ] Test `__exit__` closes client
    - [ ] Test exception handling
    - [ ] Test multiple operations in context
    - [ ] Test resource cleanup on error
- [ ] Implement `BigQueryClient` class (GREEN)
  - [ ] Add `__init__`, `__enter__`, `__exit__`
  - [ ] Convert existing functions to methods
  - [ ] Add `client` property with runtime check
- [ ] Add backward compatibility function (REFACTOR)
  - [ ] `load_movies_to_bigquery(movies, config)`
- [ ] Update flow.py to use context manager
- [ ] Verify: Coverage 0% → 80%

### 3.2 Cache Context Manager (1.5 hours)
- [ ] Write cache tests FIRST (RED)
  - [ ] Test `get_cache()` context manager
  - [ ] Test cleanup on exit
  - [ ] Test cleanup on exception
- [ ] Implement `get_cache()` in scraper.py (GREEN)
- [ ] Update scraper to use context (optional, for future use)
- [ ] Document cache TTL and directory in docstrings

## Phase 4: Flow Tests (3 hours)

### 4.1 GratisTorrent Flow Tests (1.5 hours)
- [ ] Write flow tests FIRST (RED)
  - [ ] `test_gratis_flow_execution.py`:
    - [ ] Test successful scrape and load
    - [ ] Test scrape failure (retry behavior)
    - [ ] Test load failure (retry behavior)
    - [ ] Test cache policy (1-hour TTL)
    - [ ] Test JSONL file creation
- [ ] Update `flow.py` if needed to support testing (GREEN)
- [ ] Verify: Flow coverage 0% → 80%

### 4.2 Comando Flow Tests (1.5 hours)
- [ ] Write comando flow tests (RED)
  - [ ] `test_comando_flow_execution.py`:
    - [ ] Test scrape and save to JSON
    - [ ] Test quality validation
    - [ ] Test local file output
- [ ] Update flow if needed (GREEN)
- [ ] Verify: Flow coverage 0% → 80%

## Phase 5: Async HTTP Client (5 hours)

### 5.1 Add httpx Dependency (5 min)
- [ ] Run: `uv add httpx`
- [ ] Verify: `uv run python -c "import httpx"`

### 5.2 Async HTTP Client (2 hours)
- [ ] Write async HTTP tests FIRST (RED)
  - [ ] `test_async_http_client.py`:
    - [ ] Test context manager lifecycle
    - [ ] Test single page fetch
    - [ ] Test concurrent fetches with `fetch_many()`
    - [ ] Test timeout handling
    - [ ] Test error handling
    - [ ] Test connection pooling limits
- [ ] Create `scrapers/gratis_torrent/async_http_client.py` (GREEN)
  - [ ] Implement `AsyncHTTPClient` class
  - [ ] Add `__aenter__`, `__aexit__`
  - [ ] Add `fetch_page()` and `fetch_many()` methods
- [ ] Verify: All tests pass

### 5.3 Async Scraper (2.5 hours)
- [ ] Write async scraper tests FIRST (RED)
  - [ ] `test_async_scraper.py`:
    - [ ] Test concurrent movie scraping
    - [ ] Test error handling (partial failures)
    - [ ] Test quality validation
    - [ ] Test performance (mock timing)
- [ ] Create `scrapers/gratis_torrent/async_scraper.py` (GREEN)
  - [ ] Implement `scrape_all_movies_async()`
  - [ ] Add sync wrapper `scrape_all_movies_sync_wrapper()`
- [ ] Add to public API in `__init__.py`
- [ ] Update documentation

### 5.4 Performance Benchmark (30 min)
- [ ] Create simple benchmark script
- [ ] Compare sync vs async scraping (10 movies sample)
- [ ] Document results in PR description

## Phase 6: Coverage Push & Polish (2 hours)

### 6.1 Parser Coverage (45 min)
- [ ] Add missing parser tests:
  - [ ] Test `parse_movie_page()` with complete HTML
  - [ ] Test `clean_genre()` function
  - [ ] Test malformed HTML handling
- [ ] Target: 24% → 90%

### 6.2 HTTP Client Coverage (30 min)
- [ ] Add missing HTTP client tests:
  - [ ] Test `fetch_page()` timeout behavior
  - [ ] Test encoding issues
  - [ ] Test network errors
- [ ] Target: 28% → 100%

### 6.3 Final Verification (45 min)
- [ ] Run full test suite: `uv run pytest scrapers/ -v --cov=scrapers --cov-report=term-missing`
- [ ] Verify coverage ≥80%
- [ ] Run type checker: `uvx mypy --ignore-missing-imports .`
- [ ] Run linter: `uvx ruff check --fix . && uvx ruff format --line-length 120 .`
- [ ] Test public API imports work
- [ ] Run integration tests (both scrapers)
- [ ] Update README with new API examples

## Post-Implementation

- [ ] Update this tasks.md - Mark all as [x]
- [ ] Run `openspec validate refactor-module-best-practices-tdd --strict`
- [ ] Create PR with detailed description
- [ ] After deployment: Run `openspec archive refactor-module-best-practices-tdd`
