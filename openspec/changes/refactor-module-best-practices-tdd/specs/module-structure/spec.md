## ADDED Requirements

### Requirement: Public API Exports

The package SHALL expose a curated public API through `__init__.py` files with explicit `__all__` declarations.

#### Scenario: Root package convenience imports
- **WHEN** user imports from root package
- **THEN** high-level scraper functions are available
- **EXAMPLE**: `from scrapers import scrape_gratis_torrent, scrape_comando`

#### Scenario: Utils package shared imports
- **WHEN** user imports from utils package
- **THEN** common models, validators, and parsers are available
- **EXAMPLE**: `from scrapers.utils import Movie, DataQualityChecker, parse_rating`

#### Scenario: Scraper-specific imports
- **WHEN** user imports from scraper package
- **THEN** scraper functions, config, and clients are available
- **EXAMPLE**: `from scrapers.gratis_torrent import scrape_movies, BigQueryClient`

#### Scenario: __all__ prevents wildcard pollution
- **WHEN** user does `from scrapers import *`
- **THEN** only items in `__all__` are imported (prevents internal leakage)

### Requirement: Standardized Import Patterns

All imports SHALL be at module top, following standard order: stdlib, third-party, local.

#### Scenario: No lazy imports in functions
- **WHEN** module is loaded
- **THEN** all imports occur immediately
- **THEN** no imports exist inside function bodies

#### Scenario: Import order follows convention
- **WHEN** reviewing any Python file
- **THEN** imports are grouped: stdlib, third-party, scrapers.utils, scrapers.{scraper}
- **THEN** each group is alphabetically sorted

### Requirement: Dead Code Removal

The codebase SHALL NOT contain unused modules or functions.

#### Scenario: Monitoring module deleted
- **WHEN** searching for monitoring imports
- **THEN** no references to `scrapers.utils.monitoring` exist
- **THEN** file `scrapers/utils/monitoring.py` does not exist
