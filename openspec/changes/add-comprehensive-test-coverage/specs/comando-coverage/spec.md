# Specification: Comando Torrents Scraper Test Coverage

## Overview

Complete test coverage for the Comando Torrents scraper, bringing coverage from 0% to ≥80% across all modules. Tests validate configuration, parsing, scraping logic, and flow orchestration with mocked Cloudflare bypass and local file I/O.

## ADDED Requirements

### Requirement: Configuration Loading and Validation
Tests SHALL cover configuration loading and validation for the Comando Torrents scraper. The config module has 0% coverage and MUST reach ≥90% coverage. Tests MUST verify environment variable loading, defaults, and validation.

#### Scenario: Load config from environment variables
Given environment variables set (COMANDO_BASE_URL, COMANDO_OUTPUT_PATH):
- When `ComandoConfig()` is instantiated
- Then values are read from environment
- And returned in config object
- And subsequent accesses return same values

#### Scenario: Load config with fallback defaults
Given no environment variables set:
- When `ComandoConfig()` is instantiated
- Then defaults are used (base URL, output path)
- And no exceptions raised
- And config is valid and usable

#### Scenario: Validate config with invalid values
Given invalid configuration (empty URL, non-writable path):
- When `ComandoConfig()` is instantiated with invalid values
- Then validation fails
- And error message identifies problematic field
- And exception type is clear (ValueError, ConfigError)

### Requirement: Parser Field Extraction Coverage
Tests SHALL cover movie link extraction and field parsing for the Comando Torrents parser. The parser module has 0% coverage and MUST reach ≥85% coverage. Tests MUST verify CSS selector extraction and field value parsing.

#### Scenario: Extract movie links from listing page
Given HTML listing page with article cards containing movie links:
- When parser extracts links with CSS selector `article > header > h2 > a::attr(href)`
- Then all movie URLs are found
- And URLs are properly formatted (absolute or relative)
- And order is preserved

#### Scenario: Parse movie fields from detail page
Given complete movie detail HTML with all fields:
- When parser extracts titulo, rating, link, seeds, peers, uploader, etc.
- Then all fields extract correctly
- And values are properly typed (int for seeds, float for rating)
- And None is returned for missing fields

#### Scenario: Parse movie with special characters
Given movie title with special chars: "O Retorno do Jedi: A Vingança"
- When parser extracts titulo
- Then special characters are preserved
- And no encoding issues
- And result is usable for validation

#### Scenario: Extract from malformed HTML
Given HTML with incomplete/malformed selectors:
- When parser attempts extraction
- Then missing fields return None gracefully
- And no exceptions raised
- And partial data is still usable

### Requirement: Scraper Core Logic Coverage
Tests SHALL cover fetch, parse, and cache operations in the Comando Torrents scraper. The scraper module has 0% coverage and MUST reach ≥85% coverage. Tests MUST verify Cloudflare bypass, caching, and rate limiting.

#### Scenario: Fetch page with stealth settings
Given URL and stealth session configuration:
- When `fetch_page_html(url)` is called
- Then StealthySession is used with headless=True, solve_cloudflare=True
- And HTML content is returned as string
- And URL is included in tuple (html, url)

#### Scenario: Fetch page with Cloudflare bypass
Given URL protected by Cloudflare:
- When `fetch_page_html(url)` is called with solve_cloudflare=True
- Then Cloudflare challenge is solved
- And page HTML is retrieved
- And FetchException is NOT raised

#### Scenario: Fetch page with network error
Given network connectivity issue:
- When `fetch_page_html(url)` is called
- Then exception is caught and wrapped in FetchException
- And error message includes URL and original error
- And retries happen (up to 3 attempts)

#### Scenario: Get movie links from page
Given fetched Adaptor object with listing HTML:
- When `get_movie_links(url)` is called
- Then links list is extracted via CSS selector
- And all links are returned
- And empty list returned on error (not exception)

#### Scenario: Cache memoization on repeated calls
Given same URL called twice within cache lifetime:
- When `fetch_page_html(url)` called twice
- Then second call uses cache (no HTTP request made)
- And both calls return identical HTML
- And cache decorator works correctly

#### Scenario: Rate limiter enforces 2 calls/second
Given rate limiter configured at 2 calls/second:
- When `fetch_page_html()` called in rapid succession (5x)
- Then calls are throttled
- And total time ≥ 2 seconds (5 calls at 2/sec = 2.5s min)
- And no requests exceed rate limit

### Requirement: Movie Details Scraping
Tests SHALL cover extraction and validation of movie details from individual pages. Tests MUST verify field parsing, error handling, and partial data scenarios.

#### Scenario: Scrape movie details successfully
Given valid movie detail page HTML:
- When movie details are scraped and parsed
- Then Movie object created with all available fields
- And Movie passes Pydantic validation
- And result is not None

#### Scenario: Scrape movie with missing optional fields
Given detail page missing some optional fields (sinopse, uploader):
- When scraped
- Then available fields are populated
- And missing fields are None
- And Movie object is still valid

#### Scenario: Scrape movie with parse errors
Given detail page with malformed field values:
- When scraped and parsed
- Then fields that parse successfully are included
- And fields that fail to parse are None
- And warning is logged (not error)

### Requirement: Local JSON Output and File Operations
Tests SHALL cover file I/O operations for persisting movies to JSON. Tests MUST verify JSON structure, append behavior, and error handling for file write failures.

#### Scenario: Write movies to JSON output file
Given list of 10 valid Movie objects:
- When scraper writes to `movies.json`
- Then JSON file is created with proper structure
- And all 10 movies are serialized
- And file is valid JSON (can be parsed back)

#### Scenario: Append movies to existing output
Given existing `movies.json` with 5 movies:
- When new batch of 3 movies is scraped
- Then behavior is clear (append, overwrite, deduplicate)
- And final file contains expected count
- And no data loss

#### Scenario: Handle output file write errors
Given read-only output directory:
- When scraper attempts to write JSON
- Then IOError or PermissionError is caught
- And error is logged
- And scraper continues (graceful degradation)

### Requirement: Flow Task Orchestration
Tests SHALL cover task execution and data flow for the Comando Torrents Prefect flow. The flow module has 0% coverage and MUST reach ≥80% coverage. Tests MUST verify task coordination and error handling.

#### Scenario: Run Comando flow successfully
Given mocked scraper returning 15 movies:
- When flow `run_comando_torrents()` is executed
- Then scraping task completes
- And movies are written to JSON
- And flow output includes count of movies scraped

#### Scenario: Flow handles scraper failures gracefully
Given scraper that raises exception mid-execution:
- When flow runs
- Then exception is caught
- And partial results (if any) are preserved
- And error is logged with context

#### Scenario: Flow respects rate limiting
Given rate limit of 2 requests/second:
- When flow scrapes multiple pages
- Then rate limiter is applied
- And no page fetch exceeds configured rate
- And total time reflects throttling

## MODIFIED Requirements

(None; this is new module specification)

## REMOVED Requirements

(None; additive specification)

## Coverage Targets

| Module | Current | Target | Lines to Add |
|--------|---------|--------|--------------|
| comando_torrents/config.py | 0% | 90% | 8+ tests |
| comando_torrents/parser.py | 0% | 85% | 25+ tests |
| comando_torrents/scraper.py | 0% | 85% | 30+ tests |
| comando_torrents/flow.py | 0% | 80% | 20+ tests |

## Test Files

- `scrapers/tests/unit/test_comando_config.py` (new)
- `scrapers/tests/unit/test_comando_parser.py` (new)
- `scrapers/tests/unit/test_comando_scraper.py` (new)
- `scrapers/tests/integration/test_comando_flow.py` (new)
- `scrapers/tests/fixtures/comando_html.py` (new)

## Dependencies

- pytest-loguru (for loguru log capture)
- responses (for HTTP mocking, optional)

## Notes

- StealthySession from scrapling is complex to mock; consider integration test approach with emulator or test URLs
- DiskCache mocking should use unittest.mock.patch
- Pydantic models already tested in utils; test Comando-specific field handling
