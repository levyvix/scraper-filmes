# Test Suite Quick Reference

## Running Tests

```bash
# Run complete test suite
uv run python tests/test_suite.py

# Run individual module tests
uv run python -m pytest tests/scrapers/gratis_torrent/test_parser.py
uv run python -m pytest tests/scrapers/gratis_torrent/test_models.py
uv run python -m pytest tests/scrapers/gratis_torrent/test_http_client.py
uv run python -m pytest tests/scrapers/gratis_torrent/test_config.py

# Run all pytest tests
uv run python -m pytest tests/
```

## Code Quality Checks

```bash
# Lint code
uvx ruff check .

# Format code
uvx ruff format --line-length 120 .

# Type check
uvx mypy --ignore-missing-imports .

# Run all checks (recommended before commits)
uvx ruff check . && uvx ruff format --line-length 120 . && uvx mypy --ignore-missing-imports .
```

## Test Categories

| Test | Purpose | File |
|------|---------|------|
| Module Imports | Verify all modules load | `test_suite.py` |
| Pydantic Validation | Test data validation rules | `test_suite.py` |
| Configuration | Test BigQuery config | `test_suite.py` |
| Parser Functions | Test HTML parsing utilities | `test_suite.py` |
| Model Serialization | Test data conversion | `test_suite.py` |
| Prefect Flow | Test workflow structure | `test_suite.py` |
| HTTP Client | Test web scraping utilities | `test_suite.py` |
| BigQuery Schema | Validate schema file | `test_suite.py` |

## Expected Test Count

- **Total Tests:** 8
- **Expected Pass:** 8
- **Expected Fail:** 0

## Common Issues

### Import Errors
```bash
# Fix: Ensure dependencies installed
uv sync
```

### Config Errors
```bash
# Fix: Check .env file exists with:
GCP_PROJECT_ID=your-project-id
```

### Schema Errors
```bash
# Fix: Verify schema file exists:
ls src/scrapers/gratis_torrent/schema.json
```

## Files Changed in Migration

### Updated
- `tests/test_suite.py` - Complete rewrite
- `tests/README.md` - Full documentation update

### Created
- `tests/MIGRATION_SUMMARY.md` - Detailed migration notes
- `tests/QUICK_REFERENCE.md` - This file

### Removed (from tests)
- Database schema tests
- Database insertion tests
- Deduplication tests
- Environment loading tests
- Old Prefect flow tests

## Test Output Format

```
============================================================
TEST: 1. Importações dos Módulos
============================================================
Testando importações...
  ✓ src.scrapers.gratis_torrent.models
  ✓ src.scrapers.gratis_torrent.parser
  [...]
✅ PASSOU
```

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Tests fail after git pull | Run `uv sync` |
| Import errors | Check Python path includes project root |
| Config errors | Verify `.env` file and GCP_PROJECT_ID |
| Schema errors | Check `schema.json` exists and is valid JSON |
| Flow test fails | Verify new flow structure in `flow.py` |

## Documentation Links

- Full Test Docs: `tests/README.md`
- Migration Details: `tests/MIGRATION_SUMMARY.md`
- Project Guidelines: `CLAUDE.md`
- Scraper Docs: `src/scrapers/gratis_torrent/README.md`

## Test Development

### Add New Test

1. Create test function in `test_suite.py`:
   ```python
   def test_new_feature():
       """Test description"""
       print("Testing new feature...")
       # test logic
       print("  ✓ Success")
   ```

2. Register in `main()`:
   ```python
   runner.test("9. New Feature", test_new_feature)
   ```

3. Run tests:
   ```bash
   uv run python tests/test_suite.py
   ```

## Architecture Notes

**Current:** Direct BigQuery Pipeline
- Scrape → Validate → BigQuery
- No local database
- Pydantic validation
- BigQuery MERGE for deduplication

**Legacy (removed):** SQLite → BigQuery
- Scrape → SQLite → Export → BigQuery
- Local database
- SQLAlchemy models
- Manual deduplication

## Test Timing

- Complete suite: ~2-3 seconds
- Individual tests: <1 second each
- No network calls (uses mocked data)
- No actual database operations

## Maintenance

### Run Tests Before
- Commits
- Pull requests
- Deployments
- After dependency updates
- After architecture changes

### Update Tests When
- Adding new features
- Changing data models
- Modifying configuration
- Updating BigQuery schema
- Refactoring code

## Exit Codes

- `0` - All tests passed
- `1` - One or more tests failed

Use in scripts:
```bash
uv run python tests/test_suite.py && echo "Success!" || echo "Failed!"
```
