# Test Tracking & Coverage Documentation

This document tracks which tests are working and what coverage has been achieved. It's updated as tests are implemented to avoid re-running the full suite unnecessarily during development.

**Last Updated**: 2025-11-22

---

## Overview

The comprehensive test coverage project aims to reach **≥80% overall coverage** across all scraper modules:
- **GratisTorrent Scraper**: ≥85% (parser ≥90%, flow ≥85%, BigQuery ≥80%)
- **Comando Torrents Scraper**: ≥80% (all modules)
- **Shared Utilities**: ≥80% (data_quality ≥85%, send_mail ≥80%)

---

## Test Execution Strategy

### Phase-Based Testing
Instead of running all tests at once, tests are grouped by phase and execution level:

1. **Unit tests** - Run individually by module during development
2. **Integration tests** - Run after each phase completes
3. **Coverage verification** - Run targeted coverage reports for changed modules only
4. **Full suite** - Run only when all implementation is complete (Phase 4)

### Commands for Targeted Testing

```bash
# Run a single test file (fastest, for active development)
uv run pytest scrapers/tests/unit/test_data_quality.py -v

# Run tests for a specific module with coverage
uv run pytest scrapers/tests/ -k "data_quality" -v --cov=scrapers.utils.data_quality

# Run a specific test phase/category
uv run pytest scrapers/tests/unit/ -v  # All unit tests
uv run pytest scrapers/tests/integration/ -v  # All integration tests

# Full suite (Phase 4 only)
uv run pytest scrapers/ --cov=scrapers --cov-report=term-missing
```

---

## Phase 1: Test Infrastructure & Shared Utilities

### Status: 🟡 IN PROGRESS

### Task 1.1: Fix Existing Test Issues
- **Status**: ⏳ PENDING
- **Command**: `uv run pytest scrapers/tests/unit/test_gratis_scraper.py -v`
- **Expected Result**: All 32 passing tests + 7 fixed tests = 39 passing
- **Coverage Target**: Maintain existing coverage

### Task 1.2: Create Shared Test Fixtures
- **Status**: ⏳ PENDING
- **Files to Create**:
  - `scrapers/tests/fixtures/test_data.py` - Movie objects (valid/invalid/partial)
  - `scrapers/tests/fixtures/mock_responses.py` - Mocked API responses
  - `scrapers/tests/fixtures/gratis_html.py` - GratisTorrent HTML samples
  - `scrapers/tests/fixtures/comando_html.py` - Comando Torrents HTML samples
  - `scrapers/tests/fixtures/conftest.py` - Pytest shared configuration
- **Command**: `uv run pytest scrapers/tests/fixtures/ -v --collect-only`
- **Expected Result**: All fixtures discoverable and importable

### Task 1.3: Add Data Quality Tests
- **Status**: ⏳ PENDING
- **File**: `scrapers/tests/unit/test_data_quality.py`
- **Coverage Target**: ≥85% of `scrapers/utils/data_quality.py`
- **Command**: `uv run pytest scrapers/tests/unit/test_data_quality.py -v --cov=scrapers.utils.data_quality --cov-report=term-missing`
- **Expected Result**: 35+ tests passing, coverage ≥85%

### Task 1.4: Add Send Mail Tests
- **Status**: ⏳ PENDING
- **File**: `scrapers/tests/unit/test_send_mail.py`
- **Coverage Target**: ≥80% of `scrapers/utils/send_mail.py`
- **Command**: `uv run pytest scrapers/tests/unit/test_send_mail.py -v --cov=scrapers.utils.send_mail --cov-report=term-missing`
- **Expected Result**: 20+ tests passing, coverage ≥80%

### Task 1.5: Ensure Exception Tests Pass
- **Status**: ⏳ PENDING
- **File**: `scrapers/tests/unit/test_exceptions.py` (verify exists)
- **Coverage Target**: 100% of `scrapers/utils/exceptions.py`
- **Command**: `uv run pytest scrapers/tests/unit/test_exceptions.py -v --cov=scrapers.utils.exceptions`
- **Expected Result**: All tests passing, 100% coverage maintained

---

## Phase 2: GratisTorrent Scraper Coverage

### Status: 🔴 NOT STARTED

### Task 2.1: Enhance Parser Tests
- **Status**: ⏳ PENDING
- **File**: `scrapers/tests/unit/test_gratis_parser.py`
- **Current Coverage**: 36%
- **Target Coverage**: ≥90%
- **Command**: `uv run pytest scrapers/tests/unit/test_gratis_parser.py -v --cov=scrapers.gratis_torrent.parser --cov-report=term-missing`
- **Expected Result**: 40+ new tests passing, coverage ≥90%

### Task 2.2: Enhance HTTP Client Tests
- **Status**: ⏳ PENDING
- **File**: `scrapers/tests/unit/test_gratis_http_client.py`
- **Current Coverage**: 100%
- **Target Coverage**: 100% (maintain + add edge cases)
- **Command**: `uv run pytest scrapers/tests/unit/test_gratis_http_client.py -v --cov=scrapers.gratis_torrent.http_client`
- **Expected Result**: Additional edge case tests, 100% coverage maintained

### Task 2.3: Enhance Flow Integration Tests
- **Status**: ⏳ PENDING
- **File**: `scrapers/tests/integration/test_gratis_flow.py`
- **Current Coverage**: 43%
- **Target Coverage**: ≥85%
- **Command**: `uv run pytest scrapers/tests/integration/test_gratis_flow.py -v --cov=scrapers.gratis_torrent.flow --cov-report=term-missing`
- **Expected Result**: 15+ new tests passing, coverage ≥85%

### Task 2.4: Add BigQuery Integration Tests
- **Status**: ⏳ PENDING
- **File**: `scrapers/tests/integration/test_bigquery.py`
- **Current Coverage**: 14%
- **Target Coverage**: ≥80%
- **Command**: `uv run pytest scrapers/tests/integration/test_bigquery.py -v --cov=scrapers.gratis_torrent.bigquery_client --cov-report=term-missing`
- **Expected Result**: 30+ new tests passing, coverage ≥80%

### Task 2.5: Verify Config Tests
- **Status**: ✅ COMPLETE (100% coverage - no changes needed)
- **File**: `scrapers/tests/unit/test_config.py`
- **Coverage**: 100%

---

## Phase 3: Comando Torrents Scraper Coverage

### Status: 🔴 NOT STARTED

### Task 3.1: Create Config Tests
- **Status**: ⏳ PENDING
- **File**: `scrapers/tests/unit/test_comando_config.py`
- **Current Coverage**: 0%
- **Target Coverage**: ≥90%
- **Command**: `uv run pytest scrapers/tests/unit/test_comando_config.py -v --cov=scrapers.comando_torrents.config --cov-report=term-missing`
- **Expected Result**: 8+ tests passing, coverage ≥90%

### Task 3.2: Create Parser Tests
- **Status**: ⏳ PENDING
- **File**: `scrapers/tests/unit/test_comando_parser.py`
- **Current Coverage**: 0%
- **Target Coverage**: ≥85%
- **Command**: `uv run pytest scrapers/tests/unit/test_comando_parser.py -v --cov=scrapers.comando_torrents.parser --cov-report=term-missing`
- **Expected Result**: 25+ tests passing, coverage ≥85%

### Task 3.3: Create Scraper Tests
- **Status**: ⏳ PENDING
- **File**: `scrapers/tests/unit/test_comando_scraper.py`
- **Current Coverage**: 0%
- **Target Coverage**: ≥85%
- **Command**: `uv run pytest scrapers/tests/unit/test_comando_scraper.py -v --cov=scrapers.comando_torrents.scraper --cov-report=term-missing`
- **Expected Result**: 30+ tests passing, coverage ≥85%

### Task 3.4: Create Flow Tests
- **Status**: ⏳ PENDING
- **File**: `scrapers/tests/integration/test_comando_flow.py`
- **Current Coverage**: 0%
- **Target Coverage**: ≥80%
- **Command**: `uv run pytest scrapers/tests/integration/test_comando_flow.py -v --cov=scrapers.comando_torrents.flow --cov-report=term-missing`
- **Expected Result**: 20+ tests passing, coverage ≥80%

---

## Phase 4: Integration & Validation

### Status: 🔴 NOT STARTED

### Task 4.1: Run Full Coverage Report
- **Status**: ⏳ PENDING
- **Command**: `uv run pytest scrapers/ --cov=scrapers --cov-report=term-missing --cov-report=html`
- **Expected Result**: Overall coverage ≥80%, all module targets met
- **Coverage Targets**:
  - Overall: ≥80%
  - GratisTorrent: ≥85%
  - Comando Torrents: ≥80%
  - Utils: ≥80%
  - No module <70%

### Task 4.2: Fix Coverage Gaps
- **Status**: ⏳ PENDING
- **Process**: Identify and fix untested lines/branches
- **Command**: Review `htmlcov/index.html` after coverage report
- **Expected Result**: All modules meet coverage targets

### Task 4.3: Verify All Tests Pass
- **Status**: ⏳ PENDING
- **Command**:
  - `uv run pytest scrapers/ -v`
  - `uv run pytest scrapers/ -v` (run 2-3 times to check for flakes)
- **Expected Result**: All tests pass, no skipped tests, deterministic results

### Task 4.4: Update Test Documentation
- **Status**: ⏳ PENDING
- **File**: `scrapers/tests/README.md`
- **Contents**:
  - Coverage target table (by module)
  - Fixture usage and location
  - Test patterns and examples
  - How to run tests with coverage
  - List of test files and coverage areas
  - Workarounds (pytest-loguru, etc.)

### Task 4.5: Final Validation
- **Status**: ⏳ PENDING
- **Commands**:
  - `uv run pytest scrapers/ --cov=scrapers --cov-report=term-missing | grep -E "^(Name|TOTAL|scrapers)"`
  - `uvx mypy --ignore-missing-imports scrapers/tests/`
  - `uvx ruff check scrapers/tests/`
- **Expected Result**: All checks pass, TOTAL ≥80%

---

## Coverage Summary by Module

| Module | Current | Target | Status |
|--------|---------|--------|--------|
| **scrapers.utils.data_quality** | 18% | 85% | 🔴 PENDING |
| **scrapers.utils.send_mail** | 0% | 80% | 🔴 PENDING |
| **scrapers.utils.exceptions** | 100% | 100% | 🟢 READY |
| **scrapers.utils.parse_utils** | 100% | 100% | 🟢 READY |
| **scrapers.utils.rate_limiter** | 100% | 100% | 🟢 READY |
| **scrapers.gratis_torrent.parser** | 36% | 90% | 🔴 PENDING |
| **scrapers.gratis_torrent.http_client** | 100% | 100% | 🟢 READY |
| **scrapers.gratis_torrent.config** | 100% | 100% | 🟢 READY |
| **scrapers.gratis_torrent.scraper** | 100% | 100% | 🟢 READY |
| **scrapers.gratis_torrent.flow** | 43% | 85% | 🔴 PENDING |
| **scrapers.gratis_torrent.bigquery_client** | 14% | 80% | 🔴 PENDING |
| **scrapers.comando_torrents.config** | 0% | 90% | 🔴 PENDING |
| **scrapers.comando_torrents.parser** | 0% | 85% | 🔴 PENDING |
| **scrapers.comando_torrents.scraper** | 0% | 85% | 🔴 PENDING |
| **scrapers.comando_torrents.flow** | 0% | 80% | 🔴 PENDING |
| **OVERALL** | 61% | 80% | 🔴 PENDING |

---

## Test Execution Log

This section records each test run to avoid repeating the same tests.

### Run 1: Initial Setup (Task 1.1 - Fix Existing Tests)
- **Date**: [TBD]
- **Command**: `uv run pytest scrapers/tests/unit/test_gratis_scraper.py -v`
- **Result**: [TBD]
- **Coverage**: [TBD]

### Run 2: Phase 1.2 Fixtures
- **Date**: [TBD]
- **Command**: `uv run pytest scrapers/tests/fixtures/ -v --collect-only`
- **Result**: [TBD]

### Run 3: Phase 1.3 Data Quality Tests
- **Date**: [TBD]
- **Command**: `uv run pytest scrapers/tests/unit/test_data_quality.py -v --cov=scrapers.utils.data_quality`
- **Result**: [TBD]
- **Coverage**: [TBD]

---

## Notes & Workarounds

### Loguru + Pytest Caplog Issue
- **Problem**: Loguru sends logs to stderr, not Python logging, so `caplog` doesn't capture them
- **Solution**: Install pytest-loguru: `uv add pytest-loguru --group dev`
- **Status**: [TBD - Apply in Task 1.1]

### BigQuery Mocking Strategy
- Use `unittest.mock.patch('google.cloud.bigquery.Client')`
- Mock all responses to avoid real BigQuery calls
- Document setup for BigQuery emulator (future enhancement)

### Test Determinism
- All tests must be deterministic (no flaky tests)
- Verify by running each test phase 2-3 times
- Document any timing-dependent tests

---

## Development Tips

1. **During active development**: Run only the specific test file you're working on
   - Example: `uv run pytest scrapers/tests/unit/test_data_quality.py -v`

2. **After completing a phase**: Run all tests in that phase to catch integration issues
   - Example: `uv run pytest scrapers/tests/unit/ -v`

3. **Before committing**: Run the full suite ONCE
   - Command: `uv run pytest scrapers/ --cov=scrapers --cov-report=term-missing`
   - Check that coverage ≥80% and all tests pass

4. **Don't repeat test runs** during development
   - Use this document to track what's been tested
   - Update coverage summary as you complete tasks

5. **Coverage reports**: Generate HTML for detailed analysis
   - Command: `uv run pytest scrapers/ --cov=scrapers --cov-report=html`
   - Open `htmlcov/index.html` in browser to see uncovered lines
