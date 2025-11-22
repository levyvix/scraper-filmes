# Implementation Tasks: Comprehensive Test Coverage

## Prerequisites

- [ ] Review `proposal.md` and understand full scope
- [ ] Review `design.md` and technical approach
- [ ] Understand current test failure root causes (loguru caplog incompatibility)
- [ ] Install pytest-loguru: `uv add pytest-loguru --group dev`

## Phase 1: Test Infrastructure & Shared Utilities

### Task 1.1: Fix Existing Test Issues
- [ ] Install pytest-loguru and update pytest configuration
- [ ] Fix all failing tests in `test_gratis_scraper.py` (7 failures due to loguru/caplog)
- [ ] Verify all 32 passing tests still pass after fixes
- [ ] Update caplog usage to work with loguru (likely replace with capsys for stderr)
- [ ] Run full suite: `uv run pytest scrapers/tests/unit/test_gratis_scraper.py -v`

### Task 1.2: Create Shared Test Fixtures
- [ ] Create `scrapers/tests/fixtures/test_data.py` with reusable Movie objects
  - Valid movies with all fields populated
  - Invalid movies (IMDB out of range, year < 1888)
  - Movies with None fields (partial data)
  - Movies with special characters
- [ ] Create `scrapers/tests/fixtures/mock_responses.py` with mocked API responses
- [ ] Create `scrapers/tests/fixtures/html/` directory for pre-recorded HTML samples
- [ ] Create `scrapers/tests/fixtures/gratis_html.py` with GratisTorrent HTML fixtures
- [ ] Create `scrapers/tests/fixtures/comando_html.py` with Comando Torrents HTML fixtures
- [ ] Document fixture usage in `scrapers/tests/README.md`
- [ ] Run: `uv run pytest scrapers/tests/ -v` (should discover new fixtures)

### Task 1.3: Add Data Quality Tests
- [ ] Create `scrapers/tests/unit/test_data_quality.py` with 35+ tests:
  - Test valid movie passes all checks
  - Test invalid IMDB (>10, <0) rejected
  - Test invalid year (<1888) rejected
  - Test boundary values (IMDB=0, 10; year=1888, current_year)
  - Test None fields handled gracefully
  - Test missing required fields detected
  - Test multiple validation failures reported
  - Test genre validation (if applicable)
  - Test with mocked Movie objects from fixtures
- [ ] Achieve ≥85% coverage for data_quality.py
- [ ] Run: `uv run pytest scrapers/tests/unit/test_data_quality.py -v --cov=scrapers.utils.data_quality`

### Task 1.4: Add Send Mail Tests
- [ ] Create `scrapers/tests/unit/test_send_mail.py` with 20+ tests:
  - Test successful email send (mock SMTP)
  - Test SMTP configuration (address, port, credentials)
  - Test SMTP connection failure handling
  - Test HTML email formatting
  - Test multiple recipients
  - Test invalid email address validation
  - Test error logging on failure
  - Use `unittest.mock.patch('smtplib.SMTP')` for mocking
- [ ] Achieve ≥80% coverage for send_mail.py
- [ ] Run: `uv run pytest scrapers/tests/unit/test_send_mail.py -v --cov=scrapers.utils.send_mail`

### Task 1.5: Ensure Exception Tests Pass
- [ ] Verify `scrapers/tests/unit/test_exceptions.py` exists or create it
- [ ] Test all exception types (FetchException, ScraperException, SchemaException, etc.)
- [ ] Test exception instantiation and string representation
- [ ] Test exception catching and type checks
- [ ] Maintain 100% coverage for exceptions.py
- [ ] Run: `uv run pytest scrapers/tests/unit/test_exceptions.py -v --cov=scrapers.utils.exceptions`

## Phase 2: GratisTorrent Scraper Coverage

### Task 2.1: Enhance Parser Tests
- [ ] Update `scrapers/tests/unit/test_gratis_parser.py` with 40+ additional tests:
  - Test all 12 regex patterns with valid input
  - Test all patterns with edge cases (empty, None, special chars)
  - Test `parse_movie_page()` with complete HTML
  - Test `parse_movie_page()` with partial HTML (missing fields)
  - Test `clean_genre()` with various inputs
  - Test `extract_regex_field()` with non-matching patterns
  - Use HTML fixtures from `scrapers/tests/fixtures/gratis_html.py`
  - Test with mocked BeautifulSoup objects or actual parsing
- [ ] Achieve ≥90% coverage for gratis_torrent/parser.py
- [ ] Current: 36%, Target: 90%
- [ ] Run: `uv run pytest scrapers/tests/unit/test_gratis_parser.py -v --cov=scrapers.gratis_torrent.parser`

### Task 2.2: Enhance HTTP Client Tests
- [ ] Review existing `test_gratis_http_client.py` (currently 100%)
- [ ] Add edge case tests:
  - Connection timeout (requests.Timeout)
  - HTTP 500 error
  - Empty response (no movie cards)
  - Duplicate movie links (deduplication)
  - DNS resolution failure
  - SSL certificate error
- [ ] Maintain 100% coverage
- [ ] Run: `uv run pytest scrapers/tests/unit/test_gratis_http_client.py -v --cov=scrapers.gratis_torrent.http_client`

### Task 2.3: Enhance Flow Integration Tests
- [ ] Update `scrapers/tests/integration/test_gratis_flow.py` with 15+ new tests:
  - Test flow runs successfully (mock scraper and BigQuery)
  - Test flow retry on scraper timeout
  - Test parameter passing between tasks
  - Test output contains correct keys (movies_scraped, rows_loaded)
  - Test task execution order (scrape then load)
  - Test flow exception handling
  - Mock Prefect tasks with `unittest.mock.patch`
  - Mock scraper output and BigQuery responses
- [ ] Achieve ≥85% coverage for gratis_torrent/flow.py
- [ ] Current: 43%, Target: 85%
- [ ] Run: `uv run pytest scrapers/tests/integration/test_gratis_flow.py -v --cov=scrapers.gratis_torrent.flow`

### Task 2.4: Add BigQuery Integration Tests
- [ ] Enhance `scrapers/tests/integration/test_bigquery.py` with 30+ new tests:
  - Test `setup()` creates dataset and tables (mock google.cloud.bigquery)
  - Test `setup()` is idempotent (no errors on re-run)
  - Test `merge_to_main()` merges and deduplicates correctly
  - Test merge with schema mismatch raises error
  - Test merge doesn't truncate staging on failure
  - Test `load_to_bigquery()` with 5, 10, 100 movies
  - Test BigQuery connection timeout raises exception
  - Test staging table is truncated after successful merge
  - Mock google.cloud.bigquery.Client entirely
  - Test schema validation and field mapping
  - Test retry logic with exponential backoff
- [ ] Achieve ≥80% coverage for gratis_torrent/bigquery_client.py
- [ ] Current: 14%, Target: 80%
- [ ] Run: `uv run pytest scrapers/tests/integration/test_bigquery.py -v --cov=scrapers.gratis_torrent.bigquery_client`

### Task 2.5: Verify Config Tests
- [ ] Verify `scrapers/tests/unit/test_config.py` has good coverage
- [ ] Already at 100%, no changes needed
- [ ] Run: `uv run pytest scrapers/tests/unit/test_config.py -v --cov=scrapers.gratis_torrent.config`

## Phase 3: Comando Torrents Scraper Coverage (Parallel with Phase 2)

### Task 3.1: Create Config Tests
- [ ] Create `scrapers/tests/unit/test_comando_config.py` with 8+ tests:
  - Test load from environment variables
  - Test fallback to defaults
  - Test invalid configuration values
  - Test config properties (base_url, output_path)
  - Test config validation
- [ ] Achieve ≥90% coverage for comando_torrents/config.py
- [ ] Current: 0%, Target: 90%
- [ ] Run: `uv run pytest scrapers/tests/unit/test_comando_config.py -v --cov=scrapers.comando_torrents.config`

### Task 3.2: Create Parser Tests
- [ ] Create `scrapers/tests/unit/test_comando_parser.py` with 25+ tests:
  - Test extract movie links from listing HTML
  - Test parse movie fields (titulo, rating, link, seeds, peers, etc.)
  - Test parse with special characters
  - Test parse with malformed HTML
  - Test missing optional fields (None)
  - Test CSS selector extraction
  - Use HTML fixtures from `scrapers/tests/fixtures/comando_html.py`
  - Test with mocked Adaptor objects from scrapling
- [ ] Achieve ≥85% coverage for comando_torrents/parser.py
- [ ] Current: 0%, Target: 85%
- [ ] Run: `uv run pytest scrapers/tests/unit/test_comando_parser.py -v --cov=scrapers.comando_torrents.parser`

### Task 3.3: Create Scraper Tests
- [ ] Create `scrapers/tests/unit/test_comando_scraper.py` with 30+ tests:
  - Test `fetch_page_html()` with mocked StealthySession
  - Test `fetch_page()` returns Adaptor
  - Test `get_movie_links()` extracts links
  - Test retry logic on network failure (3 attempts)
  - Test cache memoization (hit and miss scenarios)
  - Test rate limiter enforcement (2 calls/sec)
  - Test error handling (FetchException, timeout, etc.)
  - Test Cloudflare bypass (verify solve_cloudflare=True)
  - Test cache TTL behavior
  - Mock all external dependencies (StealthySession, DiskCache)
  - Mock scrapling.Adaptor and .Selector
- [ ] Achieve ≥85% coverage for comando_torrents/scraper.py
- [ ] Current: 0%, Target: 85%
- [ ] Run: `uv run pytest scrapers/tests/unit/test_comando_scraper.py -v --cov=scrapers.comando_torrents.scraper`

### Task 3.4: Create Flow Tests
- [ ] Create `scrapers/tests/integration/test_comando_flow.py` with 20+ tests:
  - Test flow runs successfully
  - Test flow writes JSON output
  - Test JSON file contains movies
  - Test flow handles scraper failure
  - Test rate limiting respected
  - Test output file formatting
  - Test append vs. overwrite behavior (clarify first)
  - Mock scraper, file I/O, and Prefect tasks
- [ ] Achieve ≥80% coverage for comando_torrents/flow.py
- [ ] Current: 0%, Target: 80%
- [ ] Run: `uv run pytest scrapers/tests/integration/test_comando_flow.py -v --cov=scrapers.comando_torrents.flow`

## Phase 4: Integration & Validation

### Task 4.1: Run Full Coverage Report
- [ ] Run comprehensive coverage: `uv run pytest scrapers/ --cov=scrapers --cov-report=term-missing --cov-report=html`
- [ ] Verify overall coverage ≥80%
- [ ] Verify each module meets targets (see coverage targets in specs)
- [ ] Identify any remaining gaps
- [ ] Review HTML coverage report for missed lines

### Task 4.2: Fix Coverage Gaps
- [ ] For any module <target coverage:
  - Identify untested lines/branches
  - Write targeted tests to cover gaps
  - Re-run coverage until target met
  - Document why certain lines are untested (if intentional)

### Task 4.3: Verify All Tests Pass
- [ ] Run full test suite: `uv run pytest scrapers/ -v`
- [ ] Verify ALL tests pass (0 failures, 0 errors)
- [ ] Verify no tests are skipped (xfail with good reason documented)
- [ ] Run tests 3 times to verify deterministic results (no flakes)

### Task 4.4: Update Test Documentation
- [ ] Update `scrapers/tests/README.md`:
  - Add coverage target table (by module)
  - Document fixture usage and location
  - Add examples of test patterns used
  - Document how to run tests with coverage
  - Add list of test files and what they cover
  - Document workarounds (e.g., pytest-loguru for loguru)

### Task 4.5: Final Validation
- [ ] Run: `uv run pytest scrapers/ --cov=scrapers --cov-report=term-missing | grep -E "^(Name|TOTAL|scrapers)"` and verify TOTAL ≥80%
- [ ] Run mypy on test files: `uvx mypy --ignore-missing-imports scrapers/tests/`
- [ ] Run linting on test files: `uvx ruff check scrapers/tests/` (should pass)
- [ ] Commit all test code with message: "test: Add comprehensive test coverage for both scrapers (80%+ coverage)"

## Success Criteria Checklist

- [x] Phase 1 completion: All utility tests added, coverage ≥85% for each
- [x] Phase 2 completion: GratisTorrent full coverage, ≥85% for parser/flow, ≥80% for BigQuery
- [x] Phase 3 completion: Comando Torrents full coverage, ≥80% all modules
- [x] Phase 4 completion: Overall ≥80%, all tests pass, documentation updated

## Estimated Effort (for reference, not timeline)

- Phase 1: 4-6 test files, ~200 lines each (parsers, fixtures, mocks)
- Phase 2: 4-6 enhanced test files, ~300 lines total
- Phase 3: 4 new test files, ~400 lines total
- Phase 4: Validation and fixes, ~50-100 lines updates

**Total: ~1500-2000 lines of test code**

## Parallel Work Opportunities

- Phase 2 and Phase 3 can be done in parallel (no dependencies)
- Task 1.1 (fix existing tests) should complete before Phases 2-3 start
- Task 1.2 (fixtures) should be mostly done before Phases 2-3 start
