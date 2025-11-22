# Specification: GratisTorrent Scraper Test Coverage

## Overview

Complete test coverage for the GratisTorrent scraper, bringing coverage from 36%-100% (varies by module) to ≥85% across the board. Tests validate parsing logic, HTTP client behavior, flow orchestration, and BigQuery integration.

## ADDED Requirements

### Requirement: Parser Regex Field Extraction Coverage
Tests SHALL cover all 12 regex patterns in the parser with valid and invalid inputs. The parser module currently has 36% coverage and MUST reach ≥90% coverage.

#### Scenario: Parse valid movie detail page
Given a complete HTML movie page with all fields populated:
- When `parse_movie_page(html)` is called
- Then all 12 fields extract correctly (titulo_dublado, titulo_original, link, rating, year, seeds, peers, uploader, tamanho_mb, posted_at, genre, sinopse)
- And no field is missing or malformed
- And parser returns valid Movie object

#### Scenario: Parse movie page with missing fields
Given an HTML page missing optional fields (e.g., sinopse, genre):
- When `parse_movie_page(html)` is called
- Then present fields extract correctly
- And missing fields are None or default values
- And parser returns valid Movie object (handles partial data gracefully)

#### Scenario: Extract regex field with invalid input
Given `extract_regex_field()` with a pattern that doesn't match:
- When called with pattern and HTML text
- Then returns None (no exception)
- And logging indicates no match found (optional)

#### Scenario: Clean genre string with special characters
Given genre string with extra whitespace, special chars: "  Action | Crime  "
- When `clean_genre(genre_str)` is called
- Then returns normalized string "Action | Crime" or equivalent
- And handles edge cases (empty string, None, single genre)

### Requirement: HTTP Client Error Handling and Edge Cases
Tests SHALL cover edge cases and error conditions for the HTTP client. While current coverage is 100%, additional scenario tests MUST ensure proper error handling for timeouts, connection failures, and malformed responses.

#### Scenario: Fetch page with connection timeout
Given a URL that times out after 40 seconds:
- When `fetch_page(url)` is called
- Then raises FetchException with timeout message
- And logs error at ERROR level with URL
- And caller can catch and retry

#### Scenario: Fetch page with HTTP 500 error
Given a URL that returns 500 (server error):
- When `fetch_page(url)` is called
- Then raises FetchException with status code details
- And response details are logged for debugging

#### Scenario: Collect movie links with empty page
Given an HTML page with no movie cards (CSS selector finds nothing):
- When `collect_movie_links(soup)` is called
- Then returns empty list (not None, not exception)
- And no errors logged

#### Scenario: Collect movie links with duplicate URLs
Given a page with duplicate movie links:
- When `collect_movie_links(soup)` is called
- Then deduplicates links while preserving order
- And returns unique URLs only

### Requirement: Flow Task Orchestration Coverage
Tests SHALL cover task execution order, retries, and parameter passing in the Prefect flow. The flow module has 43% coverage and MUST reach ≥85% coverage. Tests MUST verify task coordination and data flow.

#### Scenario: Run GratisTorrent flow successfully
Given a mocked scraper returning 10 movies and mocked BigQuery returning 8 rows inserted:
- When flow `run_gratis_torrent()` is executed
- Then Task 1 (scrape-movies) completes successfully
- And output contains `movies_scraped: 10`
- And Task 2 (load-to-bigquery) receives movie list
- And final output contains `rows_loaded: 8`

#### Scenario: Flow retry on scraper timeout
Given scraper task fails first attempt with timeout:
- When flow runs with 2 retries configured
- Then first attempt fails
- And second attempt is retried after delay
- And if second succeeds, flow completes successfully
- And failure logs are captured

#### Scenario: Flow task parameter passing
Given scraper produces list of movies:
- When Task 1 output is passed to Task 2
- Then BigQuery client receives exact same movie list
- And parameter mapping is preserved (no data loss)

### Requirement: BigQuery Client Integration Coverage
Tests SHALL cover CRUD operations, schema handling, and error cases for the BigQuery client. The module has 14% coverage and MUST reach ≥80% coverage. Tests MUST verify dataset setup, table creation, MERGE deduplication, and error handling.

#### Scenario: Setup dataset and tables on first run
Given empty GCP project with no dataset:
- When `BigQueryClient.setup()` is called
- Then creates `movies_raw` dataset in us-central1
- And creates `filmes` table with correct schema
- And creates `stg_filmes` staging table
- And subsequent calls are idempotent (no errors)

#### Scenario: Merge movies with deduplication by link
Given staging table with 5 movies, main table with 3 movies (2 duplicates by link):
- When `merge_to_main()` is called
- Then MERGE statement executes (merge-into pattern)
- And duplicate records are updated (not inserted)
- And new records are inserted
- And final main table has 6 unique movies (3+3 new)

#### Scenario: Merge fails due to schema mismatch
Given staging data with different schema than table:
- When `merge_to_main()` is called
- Then raises SchemaError or BigQueryError
- And error message identifies missing/extra fields
- And staging table is NOT truncated (safe rollback)

#### Scenario: BigQuery connection timeout
Given timeout connecting to BigQuery:
- When `load_to_bigquery(movies)` is called
- Then raises BigQueryException (or wrapped google.cloud exception)
- And error is logged with project ID
- And caller can retry with exponential backoff

### Requirement: Cache Behavior and TTL
Tests SHALL verify cache hit/miss behavior and TTL expiration for DiskCache. Tests MUST ensure cached results are used within the TTL window and fresh data is fetched after expiration.

#### Scenario: Cache hit within TTL window
Given scraper has recently cached results:
- When `scrape_all_movies()` is called again within 1 hour
- Then cache is hit
- And HTTP requests are NOT made (verify mock not called)
- And returned results match cached data

#### Scenario: Cache miss after TTL expiration
Given cached results older than 1 hour:
- When `scrape_all_movies()` is called
- Then cache is expired/missed
- And HTTP requests ARE made (verify mock called)
- And fresh data is cached

## MODIFIED Requirements

### Requirement: Test Infrastructure and Fixtures
Test fixtures SHALL be enhanced to support all test scenarios. Fixtures MUST provide pre-recorded HTML samples, mock objects, and test data for deterministic testing.

#### Scenario: Use pre-recorded HTML in tests
Given movie detail and listing HTML samples:
- When tests use fixtures instead of live URLs
- Then tests are deterministic and offline
- And tests run in milliseconds (not seconds)

#### Scenario: Mock Pydantic validation errors
Given invalid movie data (IMDB > 10, year < 1888):
- When tests create invalid Movie objects
- Then Pydantic raises ValidationError
- And tests verify error details (field name, constraint)

## REMOVED Requirements

(None; this is additive specification)

## Coverage Targets

| Module | Current | Target | Lines to Add |
|--------|---------|--------|--------------|
| gratis_torrent/parser.py | 36% | 90% | 40+ tests |
| gratis_torrent/flow.py | 43% | 85% | 15+ tests |
| gratis_torrent/bigquery_client.py | 14% | 80% | 30+ tests |
| gratis_torrent/http_client.py | 100% | 100% | 0 (maintain) |
| gratis_torrent/scraper.py | 100% | 100% | 0 (maintain) |

## Test Files

- `scrapers/tests/unit/test_gratis_parser.py` (enhance)
- `scrapers/tests/integration/test_gratis_flow.py` (enhance)
- `scrapers/tests/integration/test_bigquery.py` (enhance)
- `scrapers/tests/fixtures/gratis_html.py` (new)

## Dependencies

- pytest-loguru (for loguru log capture)
- responses (for HTTP mocking, optional)
