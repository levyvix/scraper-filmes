## ADDED Requirements

### Requirement: BigQuery Context Manager

BigQuery client SHALL be a context manager with automatic cleanup.

#### Scenario: Context manager lifecycle
- **WHEN** entering context: `with BigQueryClient(config) as bq:`
- **THEN** BigQuery client connection is created
- **WHEN** exiting context (normal or exception)
- **THEN** client connection is closed automatically

#### Scenario: Client operations within context
- **WHEN** using BigQueryClient in context
- **THEN** all operations (load, merge, truncate) are available as methods
- **EXAMPLE**: `bq.load_movies(movies)` returns row count

#### Scenario: Error outside context
- **WHEN** accessing client outside context manager
- **THEN** RuntimeError is raised: "must be used as context manager"

### Requirement: Cache Context Manager

Cache SHALL provide context manager for lifecycle management.

#### Scenario: Cache context cleanup
- **WHEN** using `get_cache()` context manager
- **THEN** cache is opened on enter
- **THEN** cache is closed on exit (even on exception)

### Requirement: Backward Compatibility Functions

Legacy functions SHALL remain for backward compatibility with deprecation path.

#### Scenario: Legacy load_movies_to_bigquery
- **WHEN** calling `load_movies_to_bigquery(movies, config)`
- **THEN** function internally uses context manager
- **THEN** same behavior as before (but with cleanup)
