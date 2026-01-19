## ADDED Requirements

### Requirement: Synchronous HTTP Client

Existing HTTP client SHALL remain for backward compatibility.

#### Scenario: Fetch page with timeout
- **WHEN** calling `fetch_page(url, config)`
- **THEN** page is fetched with configured timeout
- **THEN** BeautifulSoup object is returned

#### Scenario: Collect movie links with deduplication
- **WHEN** calling `collect_movie_links(soup)`
- **THEN** unique movie links are extracted and returned
- **THEN** order is preserved, duplicates removed

### Requirement: Asynchronous HTTP Client

An async HTTP client SHALL be available for concurrent requests.

#### Scenario: Async client context manager
- **WHEN** using `async with AsyncHTTPClient(config) as client:`
- **THEN** httpx async client is created with connection pooling
- **THEN** client is closed automatically on exit

#### Scenario: Concurrent page fetching
- **WHEN** calling `await client.fetch_many(urls)`
- **THEN** all URLs are fetched concurrently (respecting max_connections)
- **THEN** list of (url, soup) tuples is returned
- **THEN** failed fetches return (url, None)

#### Scenario: Connection pooling limits
- **WHEN** fetching 50 URLs with max_connections=10
- **THEN** at most 10 concurrent connections are active
- **THEN** requests are queued and processed as connections free

### Requirement: Async Scraper

An async scraper SHALL be available for concurrent movie scraping.

#### Scenario: Async scraping with quality checks
- **WHEN** calling `await scrape_all_movies_async(config)`
- **THEN** main page is fetched (sync - single request)
- **THEN** all movie pages are fetched concurrently (async)
- **THEN** movies are parsed and quality-validated
- **THEN** list of movie dicts is returned

#### Scenario: Sync wrapper for async scraper
- **WHEN** calling `scrape_all_movies_sync_wrapper(config)`
- **THEN** async scraper is run via `asyncio.run()`
- **THEN** same result as async version (blocking until complete)

#### Scenario: Performance improvement
- **WHEN** scraping 50 movies with async scraper
- **THEN** total time is <15 seconds (vs ~100s sync)
- **THEN** 10x performance improvement demonstrated
