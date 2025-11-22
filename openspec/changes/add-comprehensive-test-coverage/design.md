# Design: Test Coverage Architecture

## Testing Strategy

### Layered Approach

```
Mocks/Fixtures
    ↓
Unit Tests (functions, classes in isolation)
    ↓
Integration Tests (flows, BigQuery, file I/O)
    ↓
Coverage Report (identify gaps)
```

### Test Data Organization

#### Fixtures Directory Structure
```
scrapers/tests/fixtures/
├── html/                          # Pre-recorded HTML responses
│   ├── gratis_movie_listing.html  # Example listing page
│   ├── gratis_movie_detail.html   # Example movie detail page
│   ├── comando_movie_listing.html
│   └── comando_movie_detail.html
├── mock_responses.py              # Mock objects for API responses
├── test_data.py                   # Valid/invalid test movies
└── conftest.py                    # Shared pytest configuration
```

### Error Scenarios Covered

| Scenario | Test Location | Mock Strategy |
|----------|---------------|---------------|
| Network timeout | gratis_http_client, comando scraper | `requests.Timeout`, `FetchException` |
| HTTP errors (404, 500) | gratis_http_client | `requests.HTTPError`, status codes |
| Malformed HTML | parser (both) | Invalid/incomplete selectors |
| Pydantic validation | models tests | Invalid IMDB range, year < 1888 |
| BigQuery connection | bigquery_client | `google.cloud` mock service |
| Rate limiting | comando_torrents | Sleep/throttle verification |
| Cache hits/misses | scraper (both) | DiskCache mock |
| Flow task retries | flow tests | Simulate failures, verify retry counts |

### Coverage Gaps to Fill

#### GratisTorrent
1. **Parser** (36% → 90%):
   - Add tests for all 12 regex patterns
   - Test edge cases (empty fields, special characters, variations)
   - Test `parse_movie_page()` with partial data

2. **Flow** (43% → 85%):
   - Test task execution order
   - Verify retry logic with failures
   - Test parameter passing between tasks
   - Mock Prefect execution

3. **BigQuery Client** (14% → 80%):
   - Mock google-cloud-bigquery
   - Test staging table creation
   - Test MERGE (deduplicate by link)
   - Test schema validation and mismatch handling

#### Comando Torrents (0% → 80%)
1. **Config** (0%):
   - Load from environment
   - Verify defaults
   - Test invalid config values

2. **Parser** (0%):
   - Test movie link extraction
   - Test field parsing (titulo, rating, link, seeds, etc.)
   - Test error handling for malformed data

3. **Scraper** (0%):
   - Test `fetch_page_html()` with mocks
   - Test `get_movie_links()` with retry logic
   - Test `scrape_movie_details()` parsing
   - Test cache behavior

4. **Flow** (0%):
   - Test task coordination
   - Test JSON output file writing
   - Mock Prefect execution

#### Utilities (18% → 85%)
1. **Data Quality** (18%):
   - Test all validation methods
   - Test edge cases (boundary values for IMDB, year)
   - Test combined validators (multiple failures)

2. **Send Mail** (0%):
   - Mock SMTP connection
   - Test email formatting
   - Test error handling (SMTP failures)

### Mocking Strategy

Use `unittest.mock.patch` for:
- HTTP requests (requests library, scrapling)
- File I/O (DiskCache, JSON writes)
- Google Cloud APIs (BigQuery, Storage)
- External services (SMTP for email)

Use **fixtures** (pytest) for:
- Pre-recorded HTML samples
- Common test data (Movie objects)
- Configuration objects
- Database schemas

### Test Naming Convention

```python
# Format: test_<function>_<scenario>
def test_parse_rating_valid_float():       # Happy path
    pass

def test_parse_rating_invalid_input():    # Error case
    pass

def test_fetch_page_timeout():            # Exception case
    pass

def test_scrape_all_movies_cache_hit():   # Integration behavior
    pass
```

### Assertion Patterns

```python
# Basic assertions
assert result == expected

# Exception handling
with pytest.raises(ValueError, match="expected message"):
    function_that_raises()

# Mock verification
mock_function.assert_called_once_with(arg1, arg2)
mock_function.assert_called()

# Log verification (use caplog)
assert "expected log message" in caplog.text
```

## Implementation Order

1. **Phase 1: Shared Utilities** (no dependencies)
   - Fix loguru-caplog incompatibility (existing tests)
   - Add data_quality tests
   - Add send_mail tests

2. **Phase 2: GratisTorrent** (depends on utils)
   - Fix parser tests
   - Add HTTP client edge cases
   - Add flow orchestration tests
   - Add BigQuery integration tests

3. **Phase 3: Comando Torrents** (parallel to Phase 2)
   - Add all config tests
   - Add parser tests
   - Add scraper tests
   - Add flow tests

4. **Phase 4: Integration & Polish**
   - Verify coverage targets met
   - Fix flaky tests
   - Update documentation

## Known Issues

### Loguru + Pytest Caplog
Loguru sends logs to stderr, not Python logging. Current tests fail because `caplog.text` is empty.
- **Solution**: Use pytest-loguru plugin or capture stderr directly with capsys
- **Implementation**: Install `pytest-loguru`, update existing tests

### BigQuery Testing
Google Cloud BigQuery is hard to mock. Options:
1. Mock `google.cloud.bigquery.Client` entirely (simplest)
2. Use BigQuery emulator (complex setup, better fidelity)
3. Hybrid: Unit test with mocks, integration test with emulator

- **Decision**: Use option 1 (full mocks) for initial coverage, document setup for option 3

## Dependencies

New testing packages (via uv add):
- pytest-loguru (for loguru support)
- responses (mock HTTP library)
- unittest.mock (built-in)

## Validation

- Run `pytest scrapers/ --cov=scrapers --cov-report=term-missing` after each phase
- Ensure no tests are skipped (xfail tests must be documented)
- Verify deterministic test results (no flakes after 5 runs)
