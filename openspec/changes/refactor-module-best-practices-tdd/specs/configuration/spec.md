## ADDED Requirements

### Requirement: Centralized Constants

All configuration constants SHALL be defined in `scrapers/utils/constants.py` with type hints.

#### Scenario: Constants module provides values
- **WHEN** importing constants
- **THEN** HTTP timeouts, retry configs, and thresholds are available
- **EXAMPLE**: `from scrapers.utils.constants import HTTP_TIMEOUT_SECONDS, RETRY_MAX_ATTEMPTS`

#### Scenario: Constants use Final type
- **WHEN** attempting to reassign constant
- **THEN** type checker raises error (immutability enforced)

#### Scenario: Constants have docstrings
- **WHEN** reading constants.py
- **THEN** each constant group has explanatory docstring

### Requirement: Dependency Injection Pattern

Configuration SHALL be passed explicitly via constructor or function parameters.

#### Scenario: Config factory function
- **WHEN** calling `get_config()`
- **THEN** new GratisTorrentConfig instance is created
- **THEN** environment variables are loaded and validated

#### Scenario: Explicit config passing
- **WHEN** scraping movies
- **THEN** config is passed as parameter: `scrape_all_movies(config)`
- **THEN** no global config singleton is used

#### Scenario: Backward compatibility with defaults
- **WHEN** calling `scrape_all_movies()` without config
- **THEN** factory function is called internally: `get_config()`
- **THEN** scraping proceeds with default/env config

### Requirement: Pydantic Configuration Validation

Config classes SHALL use Pydantic with field validators and computed properties.

#### Scenario: Invalid GCP project ID rejected
- **WHEN** GCP_PROJECT_ID is empty or placeholder
- **THEN** ValidationError is raised with helpful message

#### Scenario: Computed paths use cached_property
- **WHEN** accessing config.SCHEMA_FILE multiple times
- **THEN** path is computed once and cached
- **THEN** no redundant filesystem operations
