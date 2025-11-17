# Test Suite Documentation

Comprehensive automated test suite for the Movie Scraper project.

## Overview

This test suite validates the functionality of the GratisTorrent scraper pipeline, which has been refactored to use a direct BigQuery pipeline (no SQLite database).

## What Gets Tested

### 1. Module Imports
Tests that all core modules can be imported without errors:
- `src.scrapers.gratis_torrent.models` - Pydantic data models
- `src.scrapers.gratis_torrent.parser` - HTML parsing functions
- `src.scrapers.gratis_torrent.http_client` - HTTP request handling
- `src.scrapers.gratis_torrent.scraper` - Main scraping orchestration
- `src.scrapers.gratis_torrent.bigquery_client` - BigQuery operations
- `src.scrapers.gratis_torrent.flow` - Prefect workflow
- `src.scrapers.gratis_torrent.config` - Configuration management

### 2. Pydantic Validation
Validates the Movie model data validation rules:
- Accepts valid movie data
- Rejects IMDB scores outside 0-10 range
- Rejects years before 1888
- Validates field types (float for `qualidade_video`, string for `qualidade`)
- Ensures required fields are present

### 3. Configuration Management
Tests the Config class:
- GCP_PROJECT_ID is set correctly
- Dataset and table IDs match expected values
- Location is configured properly
- `get_full_table_id()` method constructs correct table references

### 4. Parser Functions
Tests individual parsing utility functions:
- `clean_genre()` - Converts genre separators (/ to ,)
- `safe_convert_float()` - Safely converts strings to float
- `safe_convert_int()` - Safely converts strings to int
- `extract_regex_field()` - Extracts data using regex patterns

### 5. Model Serialization
Tests Pydantic model serialization:
- `model_dump()` returns proper dictionary
- All required fields are present in serialized output
- Data types are preserved correctly

### 6. Prefect Flow Structure
Validates the Prefect workflow configuration:
- Flow is properly defined
- All tasks are registered with correct names
- Retry policies are configured correctly:
  - `scrape-movies` task: 2 retries, 30s delay
  - `load-to-bigquery` task: 3 retries, 60s delay

### 7. HTTP Client Functions
Tests HTTP request and parsing utilities:
- `collect_movie_links()` extracts movie links from HTML
- Duplicate links are properly deduplicated
- Handles missing href attributes gracefully

### 8. BigQuery Schema
Validates the BigQuery table schema definition:
- Schema file exists and is valid JSON
- All required fields are present
- Data types match expectations:
  - STRING fields for titles and text
  - FLOAT64 for IMDB scores
  - INT64 for years and durations
  - BOOL for dubbed status
  - TIMESTAMP for update tracking

## Running the Tests

### Run All Tests

```bash
uv run python tests/test_suite.py
```

### Expected Output

```
============================================================
🧪 SUITE DE TESTES - SCRAPER DE FILMES
============================================================

============================================================
TEST: 1. Importações dos Módulos
============================================================
Testando importações...
  ✓ src.scrapers.gratis_torrent.models
  ✓ src.scrapers.gratis_torrent.parser
  ✓ src.scrapers.gratis_torrent.http_client
  ✓ src.scrapers.gratis_torrent.scraper
  ✓ src.scrapers.gratis_torrent.bigquery_client
  ✓ src.scrapers.gratis_torrent.flow
  ✓ src.scrapers.gratis_torrent.config
✅ PASSOU

============================================================
RESUMO DOS TESTES
============================================================
✅ Passou: 8
❌ Falhou: 0
📊 Total: 8

============================================================
🎉 TODOS OS TESTES PASSARAM!
============================================================
```

## Individual Module Tests

More granular tests are available in the `tests/scrapers/gratis_torrent/` directory:

```bash
# Test parser functions
uv run python -m pytest tests/scrapers/gratis_torrent/test_parser.py

# Test models
uv run python -m pytest tests/scrapers/gratis_torrent/test_models.py

# Test HTTP client
uv run python -m pytest tests/scrapers/gratis_torrent/test_http_client.py

# Test configuration
uv run python -m pytest tests/scrapers/gratis_torrent/test_config.py
```

## Migration Notes

### What Changed

The test suite has been updated to reflect the project's migration from SQLite to BigQuery:

**Removed Tests:**
- Database schema creation tests (SQLite-specific)
- Database insertion tests
- Deduplication tests (now handled by BigQuery)
- SQLAlchemy model tests

**Updated Tests:**
- Import tests now reference new module structure
- Added BigQuery schema validation
- Updated Prefect flow tests for new workflow structure
- Configuration tests for BigQuery-specific settings

**New Tests:**
- BigQuery schema validation
- Config class method tests
- Direct model serialization tests

### Legacy Flow

The old Prefect flow (`src/flows/prefect_flow_gratis.py`) is still present but deprecated. The new flow is at `src/scrapers/gratis_torrent/flow.py` and uses the direct BigQuery pipeline.

## Troubleshooting

### Test Failures

If tests fail, check the following:

1. **Dependencies:** Ensure all dependencies are installed:
   ```bash
   uv sync
   ```

2. **Environment Variables:** Verify `.env` file contains:
   ```
   GCP_PROJECT_ID=your-project-id
   ```

3. **Schema File:** Confirm `src/scrapers/gratis_torrent/schema.json` exists

4. **Module Structure:** Ensure all files in `src/scrapers/gratis_torrent/` are present

### Common Issues

**Import Errors:**
- Verify Python path includes project root
- Check for circular imports
- Ensure `__init__.py` files are present

**Validation Errors:**
- Check that Pydantic models match BigQuery schema
- Verify field types are consistent

**Configuration Errors:**
- Ensure environment variables are loaded
- Check file paths are absolute, not relative

## Adding New Tests

To add new tests to the suite:

1. Create a test function in `test_suite.py`:
   ```python
   def test_new_feature():
       """Test description"""
       print("Testing new feature...")

       from src.module import function

       result = function()
       assert result == expected, "Error message"

       print("  ✓ Feature works correctly")
   ```

2. Register the test in `main()`:
   ```python
   runner.test("9. New Feature", test_new_feature)
   ```

3. Run the updated suite:
   ```bash
   uv run python tests/test_suite.py
   ```

## Best Practices

1. **Isolation:** Tests should not depend on external services (no actual web scraping)
2. **Speed:** All tests should complete in under 5 seconds
3. **Cleanup:** Tests should clean up any temporary resources
4. **Clarity:** Error messages should clearly indicate what went wrong
5. **Coverage:** Test both success and failure paths

## Continuous Integration

To integrate with CI/CD pipelines:

### GitHub Actions

Create `.github/workflows/test.yml`:

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      - name: Run tests
        run: uv run python tests/test_suite.py
        env:
          GCP_PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
```

## Related Documentation

- [Project README](/README.md)
- [CLAUDE.md](/CLAUDE.md) - Development guidelines
- [GratisTorrent Scraper README](/src/scrapers/gratis_torrent/README.md)
