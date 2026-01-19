# Design Document: Python Module Best Practices & TDD

## Context

scraper-filmes is a production movie scraping system with dual scrapers (GratisTorrent and Comando Torrents). The codebase has grown organically with ad-hoc patterns, resulting in:
- 39% test coverage with critical infrastructure untested
- No public API (empty `__init__.py` files)
- Configuration scattered across 8+ files
- Sequential HTTP requests (performance bottleneck)
- Anti-patterns (lazy imports, global singletons, no resource cleanup)

This refactoring transforms the codebase into a maintainable, well-tested Python package following industry best practices.

## Goals

1. **Testability**: Achieve 80%+ coverage with TDD methodology
2. **Maintainability**: Clear public API, centralized config, standard patterns
3. **Performance**: 10x speedup with async HTTP (100s → 10s for 50 movies)
4. **Reliability**: Proper resource management (context managers, cleanup)
5. **Developer Experience**: Easy imports, dependency injection, clear documentation

## Non-Goals

- Changing core scraping logic (parsing, data models)
- Rewriting working code without justification
- Adding unnecessary abstractions or frameworks
- Breaking backward compatibility without migration path (where feasible)

## Key Decisions

### Decision 1: Dependency Injection Over Singleton

**Choice**: Replace global `Config` singleton with factory functions and explicit passing.

**Rationale**:
- **Testability**: Easy to inject mock configs in tests
- **Flexibility**: Multiple configs in same process (e.g., testing)
- **Explicitness**: Clear where config comes from
- **Type Safety**: Better IDE autocomplete and type checking

**Migration**:
```python
# Before (implicit global)
from scrapers.gratis_torrent.config import Config
movies = scrape_all_movies()  # Uses global Config

# After (explicit injection)
from scrapers.gratis_torrent.config import get_config
config = get_config()
movies = scrape_all_movies(config)

# Or with backward compat (default factory)
movies = scrape_all_movies()  # Calls get_config() internally
```

**Trade-offs**:
- ✅ Pro: Explicit dependencies, easier testing
- ✅ Pro: Supports multiple configurations
- ❌ Con: Breaking change (mitigated with default params)
- ❌ Con: More verbose (1 extra line for explicit config)

**Alternatives Considered**:
1. **Keep singleton** - Rejected: Hard to test, global state issues
2. **Environment variables only** - Rejected: No runtime validation
3. **Dependency injection framework** - Rejected: Overkill for this size

### Decision 2: Context Managers for Resource Cleanup

**Choice**: Convert BigQuery client and cache to use context managers.

**Rationale**:
- **Safety**: Guaranteed cleanup even on exceptions
- **Pythonic**: Standard pattern (`with` statement)
- **Explicit**: Clear resource lifecycle
- **No Leaks**: Connections closed automatically

**Example**:
```python
# Before (manual cleanup, error-prone)
client = get_client()
try:
    load_data(client, data)
finally:
    client.close()  # Often forgotten!

# After (automatic cleanup)
with BigQueryClient(config) as bq:
    bq.load_movies(movies)
# Client automatically closed here
```

### Decision 3: Async HTTP with httpx

**Choice**: Add async scraper using httpx for concurrent requests.

**Rationale**:
- **Performance**: 10x speedup (100s → 10s for 50 movies)
- **Modern**: httpx is the async successor to requests
- **HTTP/2**: Connection multiplexing, better performance
- **Type-Safe**: Full type hints support

**Why httpx over aiohttp**:
- ✅ Requests-compatible API (easier migration)
- ✅ HTTP/2 support out of the box
- ✅ Better type hints
- ✅ Simpler connection pooling

**Trade-offs**:
- ✅ Pro: Massive performance improvement
- ✅ Pro: No breaking changes (new feature)
- ❌ Con: New dependency (httpx)
- ❌ Con: Complexity (async/await learning curve)

### Decision 4: Centralized Constants Module

**Choice**: Create `scrapers/utils/constants.py` for all magic numbers.

**Rationale**:
- **Single Source of Truth**: One place to change timeouts, thresholds
- **Type Safety**: `Final` types prevent reassignment
- **Discoverability**: Easy to find all configurable values
- **Documentation**: Docstrings explain each constant

**What Goes in Constants**:
- ✅ Timeouts, delays, thresholds
- ✅ Retry configurations
- ✅ Data validation ranges (IMDB 0-10, year ≥1888)
- ❌ URLs, paths (stay in Config classes)
- ❌ Secrets (stay in .env)

### Decision 5: Public API Design

**Choice**: Populate `__init__.py` files with curated exports.

**Rationale**:
- **Discoverability**: Users don't need to know file structure
- **Namespace Control**: `__all__` prevents accidental exports
- **Convenience**: `from scrapers import scrape_gratis_torrent` vs deep imports
- **Semantic Versioning**: Control what's public vs internal

**API Layers**:
```python
# Layer 1: High-level convenience (root package)
from scrapers import scrape_gratis_torrent

# Layer 2: Scraper-specific (for advanced usage)
from scrapers.gratis_torrent import BigQueryClient, GratisTorrentConfig

# Layer 3: Utilities (shared across scrapers)
from scrapers.utils import Movie, DataQualityChecker
```

### Decision 6: Delete monitoring.py (Dead Code)

**Choice**: Remove `scrapers/utils/monitoring.py` completely.

**Rationale**:
- **Unused**: Grep confirms no imports anywhere
- **Overlapping**: Functionality covered by `data_quality.py`
- **Simplicity**: 97 fewer lines to maintain

## Implementation Strategy

### Phase-Based Approach

**Why Phased**:
- Incremental progress with regular validation
- Test coverage improves progressively
- Early wins build momentum
- Easier code review (smaller diffs)

**Phase Order Rationale**:
1. **Phase 0 (Emergency)**: Unblocks 200+ test lines
2. **Phase 1 (Quick Wins)**: Visible improvements, fast
3. **Phase 2 (Config)**: Foundation for later phases
4. **Phase 3 (Resources)**: Critical for production safety
5. **Phase 4 (Flows)**: Protects data pipeline
6. **Phase 5 (Async)**: Performance boost
7. **Phase 6 (Polish)**: Final coverage push

### TDD Workflow (Strict RED-GREEN-REFACTOR)

**Every change follows**:
1. **RED**: Write failing test first
2. **GREEN**: Implement minimal code to pass
3. **REFACTOR**: Improve code without breaking tests

## Risks & Mitigations

### Risk 1: Breaking Changes Impact Users

**Mitigation**:
- Provide backward compatibility wrappers where feasible
- Document migration path in proposal
- Add deprecation warnings before removing old APIs
- Include migration examples in README

### Risk 2: Async Adds Complexity

**Mitigation**:
- Keep sync scraper as default (opt-in async)
- Provide sync wrapper for async functions
- Document when to use sync vs async
- Add comprehensive async tests

### Risk 3: Test Coverage Takes Too Long

**Mitigation**:
- Focus on critical paths first (BigQuery, flows)
- Use mocking to speed up tests
- Parallelize test execution with pytest-xdist
- Accept 80% threshold (not 100%)

## Migration Plan

### Phase 1: Preparation (Before Implementation)
1. Announce breaking changes
2. Document migration examples
3. Create feature branch
4. Run baseline tests

### Phase 2: Implementation (During)
1. Implement phases sequentially
2. Keep main branch compatible (passing tests)
3. Test each phase independently
4. Document breaking changes in commits

### Phase 3: Deployment (After)
1. Merge to main with comprehensive PR description
2. Update README with new API examples
3. Send migration guide
4. Monitor for issues

### Rollback Plan

If critical issues arise:
1. Revert merge commit
2. Analyze failure in feature branch
3. Fix and re-test
4. Re-deploy when stable

**Rollback Trigger**: Any production failure or >10% test failures

## Success Criteria

### Quantitative
- ✅ Test coverage: 39% → 80%+
- ✅ Test count: 204 → 318+ (114 new tests)
- ✅ Coverage gaps: BigQuery 0% → 80%, Flows 0% → 80%
- ✅ Performance: Scraping 50 movies <15s (from 100s)
- ✅ Public API: 15+ exported functions

### Qualitative
- ✅ All `__init__.py` files have exports
- ✅ No lazy imports in functions
- ✅ Context managers for all resources
- ✅ Zero hardcoded timeouts in business logic
- ✅ TDD workflow documented and followed

### Code Quality
- ✅ MyPy strict mode passes (0 errors)
- ✅ Ruff linting passes (0 warnings)
- ✅ Pre-commit hooks pass
- ✅ All tests pass in CI
