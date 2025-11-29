# Proposal: Comprehensive Test Coverage for All Scrapers

## Why

The project currently has fragmented test coverage across scrapers and utilities, with several critical modules having no test coverage at all. This creates risk when deploying production features, making refactoring unsafe, and making it difficult to trust data quality checks. Comprehensive test coverage enables confident refactoring, early bug detection, reliable CI/CD pipelines, and executable documentation.

## What Changes

- Add 50+ new unit tests for shared utilities (data_quality, send_mail, exceptions)
- Add 40+ parser tests for GratisTorrent scraper with edge cases and HTML fixtures
- Add 30+ integration tests for BigQuery client (setup, merge, deduplication)
- Add 20+ tests for Comando Torrents scraper (config, parser, scraper, flow)
- Create reusable test fixtures for HTML samples, mock responses, and test data
- Fix existing pytest-loguru incompatibility issues (7 failing tests)
- Update test documentation with coverage targets and patterns
- Achieve ≥80% overall coverage with module-specific targets (85%+ for parsers, 80%+ for others)

## Summary

Achieve **80% minimum test coverage** across all scraper modules (gratis_torrent, comando_torrents) and utilities. Current coverage is fragmented:
- **gratis_torrent**: 36% (parser) to 100% (scraper)
- **comando_torrents**: 0% (all modules uncovered)
- **utils**: 18% (data_quality) to 100% (parse_utils, rate_limiter)
- **Overall**: 61%

This proposal introduces unit and integration tests to cover all major code paths, including error handling, edge cases, and data quality checks.

## Goals

1. **Test Coverage**: Reach ≥80% coverage across scrapers and utilities
2. **Test Quality**: Cover critical paths, error conditions, and integration scenarios
3. **Maintainability**: Tests serve as executable documentation for both scrapers
4. **CI/CD Ready**: Enable automated testing in deployment pipelines

## Scope

### In Scope
- **GratisTorrent Scraper**: Complete parsing, HTTP client, flow orchestration, and BigQuery integration
- **Comando Torrents Scraper**: Parser, scraper logic, flow orchestration (all currently untested)
- **Shared Utilities**: Data quality checks, email notifications, exception handling
- **Error Scenarios**: Network failures, malformed data, timeout handling, retries

### Out of Scope
- End-to-end live scraping against real websites (use fixtures/mocks)
- Performance benchmarking or load testing
- CI/CD pipeline configuration (covered separately)

## Approach

### Test Organization
- **Unit Tests**: Function-level testing with mocks (scrapers/tests/unit/)
- **Integration Tests**: Flow and BigQuery end-to-end (scrapers/tests/integration/)
- **Fixtures**: Reusable HTML samples, mock responses, test data (scrapers/tests/fixtures/)

### Key Test Areas

#### GratisTorrent Scraper
- Parser regex patterns and field extraction (missing 36% coverage)
- HTTP client error handling (currently 100%, maintain coverage)
- Flow task coordination and retries (missing 57% coverage)
- BigQuery staging, merge, and deduplication (missing 86% coverage)
- Cache behavior and TTL expiration

#### Comando Torrents Scraper
- All modules need coverage: config, parser, scraper, flow (0% currently)
- Stealth fetching with Cloudflare bypass
- Movie link extraction and parsing
- Local JSON output and file operations
- Cache memoization

#### Shared Utilities
- Data quality checks (missing 82% coverage): field validation, edge cases
- Email notifications (0% coverage)
- Exception hierarchy (100% coverage, maintain)

### Test Fixtures
- Pre-recorded HTML samples (saved responses)
- Mock movie data objects
- Valid/invalid Pydantic model inputs
- Config files for different environments

## Success Criteria

1. **Coverage Metrics**:
   - Overall: ≥80%
   - GratisTorrent: ≥85%
   - Comando Torrents: ≥80%
   - Utils: ≥80%
   - No individual module <70%

2. **Test Quality**:
   - All tests pass consistently (deterministic, no flakes)
   - Error scenarios tested (timeouts, network errors, validation failures)
   - Edge cases covered (empty results, malformed data, rate limits)

3. **Documentation**:
   - Test README updated with coverage requirements and patterns
   - Test fixtures documented
   - New test files include docstrings

## Related Specifications

- (None yet; testing is foundational infrastructure)

## Timeline

Not estimated; work items detailed in `tasks.md`.
