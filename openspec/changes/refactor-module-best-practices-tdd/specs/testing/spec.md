## ADDED Requirements

### Requirement: Test Coverage Threshold

The codebase SHALL maintain ≥80% test coverage.

#### Scenario: Overall coverage check
- **WHEN** running `pytest --cov=scrapers --cov-report=term-missing`
- **THEN** total coverage is ≥80%
- **THEN** no critical modules have 0% coverage

#### Scenario: Module-specific coverage
- **WHEN** checking specific modules
- **THEN** `bigquery_client.py` has ≥80% coverage
- **THEN** `flow.py` (both scrapers) has ≥80% coverage
- **THEN** `async_http_client.py` has ≥80% coverage

### Requirement: TDD Workflow

All new code SHALL be developed using test-driven development.

#### Scenario: RED-GREEN-REFACTOR cycle
- **WHEN** adding new feature
- **THEN** test is written first (RED - fails)
- **THEN** minimal code is added to pass (GREEN)
- **THEN** code is refactored without breaking tests (REFACTOR)

### Requirement: Test Independence

Tests SHALL be independent and not rely on execution order.

#### Scenario: Tests run in any order
- **WHEN** running `pytest --random-order`
- **THEN** all tests pass regardless of order

#### Scenario: Tests clean up after themselves
- **WHEN** test creates cache or files
- **THEN** cleanup occurs in fixture teardown
- **THEN** no artifacts remain after test suite

### Requirement: Comando Torrents Test Fix

Comando Torrents tests SHALL not fail on import errors.

#### Scenario: Camoufox import mocked
- **WHEN** running Comando Torrents tests
- **THEN** camoufox/Scrapling imports are mocked at session level
- **THEN** tests run successfully without browser installation
- **THEN** 200+ test lines are executable
