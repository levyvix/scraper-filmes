# Proposal: Integrate Loguru Logger with Prefect Task Logs

## Why

Currently, loguru logs are not properly integrated with Prefect's logging system. While `log_prints=True` captures some output, loguru logs miss critical Prefect metadata (task context, run ID, timestamp correlation) and don't appear in Prefect's unified task logs. This makes debugging distributed workflows difficult and prevents proper log correlation across Prefect Cloud/UI.

## What Changes

- Create Prefect-aware logging handler that bridges loguru → Prefect's `get_run_logger()`
- Update `setup_logging()` in `logging_config.py` to detect Prefect context and route logs appropriately
- Ensure all loguru calls inside Prefect tasks appear in Prefect's task run logs with full metadata
- Handle graceful degradation when running outside Prefect (local scripts, unit tests)
- Add configuration options for log levels and formats per environment

## Summary

Enable loguru logger to seamlessly integrate with Prefect's native logging system so that:
1. All loguru messages inside Prefect tasks appear in task run logs with Prefect metadata
2. Logs are visible in Prefect Cloud UI and local runs with proper context
3. Log levels can be configured per environment (local vs. Prefect Cloud)
4. Graceful fallback to console/file logging when not in Prefect context

## Goals

1. **Prefect Integration**: Loguru logs flow through Prefect's logging infrastructure
2. **Metadata Preservation**: Task context, run ID, and timestamps are preserved
3. **Environment Awareness**: Detect Prefect context and adjust logging strategy
4. **No Breaking Changes**: Existing log statements continue to work unchanged

## Scope

### In Scope
- Prefect-aware loguru handler that uses `get_run_logger()` when available
- Update `setup_logging()` to detect and handle Prefect context
- Configure log routing based on execution context (local vs. Prefect)
- Update `flow.py` and task definitions to use the integrated logger
- Add unit tests for context detection and handler selection

### Out of Scope
- Changes to existing Prefect flow structure or task definitions
- BigQuery or scraper business logic changes
- Prefect Cloud-specific features (currently testing local execution)
- Log aggregation to external services (e.g., Datadog, CloudLogging)

## Approach

### Architecture

```
Loguru Logger
    ↓
Context Detection (Are we in Prefect?)
    ├─ YES → Route to Prefect Handler (get_run_logger())
    │         ├─ Prefect task log (with metadata)
    │         └─ File log (backup)
    └─ NO → Route to Standard Handler
            ├─ Console output
            └─ File log
```

### Key Components

1. **Prefect Handler** (`logging_config.py`)
   - Custom loguru sink that calls Prefect's `get_run_logger()`
   - Handles message formatting and level mapping
   - Gracefully degrades if Prefect not available

2. **Context Detection**
   - Check if running inside Prefect task using `get_run_logger()` availability
   - Set up appropriate handlers based on context
   - Support for local testing, Prefect local execution, and Prefect Cloud

3. **Logger Configuration** (`logging_config.py`)
   - Single `setup_logging()` function that handles all contexts
   - Optional parameters for log level and file paths
   - Environment-based defaults

4. **Integration Points**
   - `flow.py`: Initialize logger once at module level
   - Task functions: Use logger normally, no changes needed
   - Unit tests: Capture logs using pytest-loguru plugin

## Success Criteria

1. **Functionality**:
   - All loguru calls inside Prefect tasks appear in task run logs
   - Logs include Prefect metadata (task name, run ID) when available
   - Console output shows logs when running locally
   - File logs capture all messages regardless of environment

2. **Compatibility**:
   - Existing code requires no changes (drop-in replacement)
   - Works in local execution, Prefect local, and Prefect Cloud
   - No breaking changes to logging API

3. **Testing**:
   - Unit tests verify context detection
   - Unit tests verify handler selection
   - Integration test: Run flow locally and verify logs appear in task logs
   - No test failures or deprecation warnings

## Related Specifications

- Requires: Python logging integration with Prefect SDK
- Related to: Comprehensive test coverage (logging in test logs)
- Complements: Flow orchestration in `flow.py`

## Timeline

Not estimated; work items detailed in `tasks.md`.
