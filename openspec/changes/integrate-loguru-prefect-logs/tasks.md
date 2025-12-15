# Tasks: Loguru + Prefect Logging Integration

## Phase 1: Core Implementation

### Task 1.1: Implement Prefect Handler in logging_config.py

**Description**: Add `prefect_handler()` function to route loguru messages to Prefect's logger.

**Steps**:
1. Add import for conditional `from prefect import get_run_logger` handling
2. Implement `prefect_handler(message)` sink function
3. Map loguru levels to Python logging levels (DEBUG→debug, INFO→info, etc.)
4. Handle RuntimeError gracefully when get_run_logger() unavailable
5. Document the function with docstring explaining behavior

**Validation**:
- Function exists in `logging_config.py`
- Handler correctly maps all 5 log levels
- No errors raised when not in Prefect context

**Dependencies**: None (Phase 1 start)

**File**: `scrapers/utils/logging_config.py`

---

### Task 1.2: Update setup_logging() to Support Prefect

**Description**: Enhance `setup_logging()` to initialize Prefect handler with context detection.

**Steps**:
1. Add optional `enable_prefect=True` parameter to `setup_logging()`
2. Keep existing console and file handler setup unchanged
3. Add Prefect handler initialization after file handler
4. Wrap Prefect handler addition in try/except for RuntimeError handling
5. Update docstring to document new parameter and Prefect integration

**Validation**:
- Function signature updated correctly
- Prefect handler is added when `enable_prefect=True` (default)
- Prefect handler is skipped when `enable_prefect=False`
- Function returns logger successfully in all cases
- No errors when `get_run_logger()` unavailable

**Dependencies**: Task 1.1 (prefect_handler function)

**File**: `scrapers/utils/logging_config.py`

---

### Task 1.3: Verify Backward Compatibility

**Description**: Ensure existing callers work unchanged.

**Steps**:
1. Run `python -m scrapers.gratis_torrent.flow` and verify it starts
2. Check that flow.py's logger initialization line remains unchanged
3. Verify logs appear in console and `gratis_torrent.log` file
4. Test command: `uv run python -m scrapers.gratis_torrent.flow 2>&1 | head -20`
5. Confirm no new exceptions or warnings

**Validation**:
- Existing code compiles without changes
- Logger is initialized successfully
- No deprecation warnings or errors
- Output includes log messages from scrapers

**Dependencies**: Task 1.2 (updated setup_logging)

**File**: `scrapers/gratis_torrent/flow.py` (verify, don't modify)

---

## Phase 2: Testing and Validation

### Task 2.1: Create Unit Tests for Context Detection

**Description**: Test that context detection works correctly in both Prefect and non-Prefect scenarios.

**Steps**:
1. Create test file: `tests/scrapers/utils/test_logging_prefect_integration.py`
2. Test 1: Import setup_logging - should not raise errors
3. Test 2: Call setup_logging() outside Prefect - verify no RuntimeError
4. Test 3: Mock Prefect context - verify Prefect handler is used
5. Test 4: Verify handler list includes Prefect handler when available
6. Test 5: Verify handler list excludes Prefect handler when enable_prefect=False

**Validation**:
- All 5 tests pass
- Coverage for prefect_handler() function
- No test failures when run with: `uv run pytest tests/scrapers/utils/test_logging_prefect_integration.py -v`

**Dependencies**: Phase 1 (implementation complete)

**Files**:
- Create: `tests/scrapers/utils/test_logging_prefect_integration.py`

---

### Task 2.2: Create Unit Tests for Handler Behavior

**Description**: Test that loguru messages are correctly routed and formatted.

**Steps**:
1. Create test file: `tests/scrapers/utils/test_loguru_handler.py`
2. Test 1: Verify message reaches console handler
3. Test 2: Verify message reaches file handler
4. Test 3: Verify all log levels are handled (DEBUG, INFO, WARNING, ERROR, CRITICAL)
5. Test 4: Verify log format includes timestamp, level, and message
6. Test 5: Mock Prefect and verify message reaches prefect_logger

**Validation**:
- All 5 tests pass
- File logs contain expected messages with correct format
- No errors when using pytest-loguru plugin: `uv run pytest tests/scrapers/utils/test_loguru_handler.py -v`

**Dependencies**: Task 2.1 (context detection tests)

**Files**:
- Create: `tests/scrapers/utils/test_loguru_handler.py`

---

### Task 2.3: Test Backward Compatibility in Test Suite

**Description**: Verify existing tests still pass with new logging setup.

**Steps**:
1. Run existing test suite: `uv run pytest tests/scrapers/ -v`
2. Check for any deprecation warnings or errors related to logging
3. Verify `log_prints=True` in task definitions still works
4. Confirm all tests pass (or document any pre-existing failures)

**Validation**:
- No new test failures introduced
- Existing log capturing via caplog/capsys still works
- Test output shows no loguru-related warnings

**Dependencies**: All Phase 1 and 2.1, 2.2 tasks

**File**: `tests/scrapers/` (existing test suite)

---

## Phase 3: Integration and Documentation

### Task 3.1: Manual Integration Test - Local Execution

**Description**: Verify logs appear correctly when running flow locally.

**Steps**:
1. Run flow locally: `uv run python -m scrapers.gratis_torrent.flow`
2. Verify console output includes log messages
3. Verify `gratis_torrent.log` file contains messages
4. Check that messages appear from all components (scraper, flow, etc.)
5. Document what logs look like at each level

**Validation**:
- Console shows INFO and above messages
- File shows DEBUG and above messages
- No errors in execution
- Messages are readable and include all context

**Dependencies**: Phase 1 (implementation)

**Manual Testing Required**: Yes

---

### Task 3.2: Update logging_config.py Docstring

**Description**: Document the Prefect integration feature and behavior.

**Steps**:
1. Update module docstring to mention Prefect integration
2. Add docstring to `prefect_handler()` explaining its role
3. Update `setup_logging()` docstring with `enable_prefect` parameter
4. Add section explaining behavior in Prefect vs. non-Prefect contexts
5. Add examples showing usage in both contexts

**Validation**:
- Docstrings are clear and accurate
- Examples compile and run
- No typos or formatting issues

**Dependencies**: Phase 1 (implementation)

**File**: `scrapers/utils/logging_config.py`

---

### Task 3.3: Create Change Log Entry

**Description**: Document this change for project history.

**Steps**:
1. Create entry in CHANGELOG.md (if exists) or in commit message
2. Summarize: "Integrate Loguru logger with Prefect task logging"
3. Mention: Logs now appear in Prefect's task run logs with metadata
4. Note: Backward compatible, no code changes required
5. Link to OpenSpec change: `openspec/changes/integrate-loguru-prefect-logs`

**Validation**:
- Entry is clear and accurate
- Can be read by project maintainers

**Deliverable**: Commit message or CHANGELOG.md entry

---

## Phase 4: Validation and Review

### Task 4.1: Validate OpenSpec Proposal

**Description**: Ensure all OpenSpec requirements are met.

**Steps**:
1. Run: `openspec validate integrate-loguru-prefect-logs --strict`
2. Fix any validation errors (missing scenarios, dangling references, etc.)
3. Verify all requirements have scenarios
4. Verify all scenarios are testable
5. Document any edge cases discovered

**Validation**:
- OpenSpec validation passes
- No warnings or errors
- All requirements are verifiable

**Deliverable**: Output of `openspec validate` command

---

### Task 4.2: Code Review Checklist

**Description**: Review implementation against specification.

**Checklist**:
- [ ] Prefect handler correctly routes loguru to get_run_logger()
- [ ] Context detection is silent (no errors when not in Prefect)
- [ ] All log levels are mapped correctly
- [ ] Backward compatibility maintained (no changes to existing code)
- [ ] Error handling is resilient (doesn't crash on Prefect logger failures)
- [ ] Unit tests cover context detection and handler behavior
- [ ] Integration tests verify end-to-end behavior
- [ ] Docstrings are clear and accurate
- [ ] No new warnings or deprecations introduced

**Validation**: Review checklist

---

### Task 4.3: Final Testing Run

**Description**: Run complete test suite to ensure all requirements are met.

**Steps**:
1. Run linter: `uvx ruff check .`
2. Run formatter: `uvx ruff format --line-length 120 .`
3. Run type checker: `uvx mypy --ignore-missing-imports .`
4. Run tests: `uv run pytest tests/ -v --cov=scrapers --cov-report=term-missing`
5. Run flow manually: `uv run python -m scrapers.gratis_torrent.flow`
6. Verify no new failures or warnings

**Validation**:
- All checks pass
- No new test failures
- Coverage maintained or improved
- No deprecation warnings

---

## Parallelizable Work

**Independent tasks** (can run in parallel):
- Task 2.1 and 2.2 (unit tests can be written simultaneously)
- Task 3.2 and 3.3 (documentation and changelog can be updated in parallel)

**Sequential dependencies**:
1. Phase 1 (implementation) must complete first
2. Phase 2 (testing) depends on Phase 1
3. Phase 3 (integration) depends on Phase 1
4. Phase 4 (validation) depends on all previous phases

## Estimated Effort

- Phase 1: ~2 hours (implementation)
- Phase 2: ~3 hours (unit tests, 3 test files)
- Phase 3: ~1 hour (integration, documentation)
- Phase 4: ~1 hour (validation, review)

**Total**: ~7 hours of focused work

## Success Definition

✅ OpenSpec validation passes
✅ All unit tests pass
✅ All integration tests pass
✅ Existing tests still pass (backward compatible)
✅ Logs appear in Prefect when running in Prefect context
✅ Logs appear in console/file when running locally
✅ No code changes required in existing modules
✅ Documentation is clear and accurate
