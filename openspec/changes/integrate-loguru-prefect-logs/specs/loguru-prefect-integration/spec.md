# Specification: Loguru + Prefect Logging Integration

## Overview

Enable loguru logger to seamlessly integrate with Prefect's native logging system so all loguru messages inside Prefect tasks appear in task run logs with full Prefect metadata.

## ADDED Requirements

### Requirement: Prefect-Aware Log Handler

The system SHALL route loguru messages to Prefect's `get_run_logger()` when running inside a Prefect task to ensure logs appear in the task run logs with proper metadata.

#### Scenario: Loguru routes to Prefect logger in task context

Given a Prefect task is executing
When a loguru logger call is made (e.g., `logger.info("message")`)
Then the message is delivered to Prefect's `get_run_logger()`
And the log appears in the Prefect task run log with task context metadata
And the log level is correctly mapped (DEBUG → debug(), INFO → info(), etc.)

#### Scenario: Loguru gracefully falls back when not in Prefect context

Given loguru is initialized outside a Prefect task (local script, unit test)
When a loguru logger call is made
Then the handler detects the absence of Prefect context (RuntimeError from get_run_logger())
And the message is NOT passed to Prefect (no error raised)
And the message still reaches other handlers (console, file)

#### Scenario: Log levels are correctly mapped

Given a loguru message at level X
When it is sent to Prefect's logger
Then it is mapped to the corresponding Python logging level:
  - DEBUG → debug()
  - INFO → info()
  - WARNING → warning()
  - ERROR → error()
  - CRITICAL → critical()

### Requirement: Context Detection

The logging system SHALL automatically detect whether it is running inside Prefect and configure handlers accordingly.

#### Scenario: Detect Prefect context by attempting get_run_logger()

Given `setup_logging()` is called
When it tries to call `prefect.get_run_logger()`
Then:
  - If successful → Initialize Prefect handler ✓
  - If RuntimeError → Skip Prefect handler, continue with others ✓
And the detection is silent (no errors logged)

#### Scenario: Prevent handler initialization errors

Given Prefect handler is being initialized
When `get_run_logger()` raises RuntimeError (not in Prefect context)
Then the exception is caught
And the function continues normally
And existing handlers (console, file) remain active

### Requirement: Unified setup_logging() Function

A single `setup_logging()` function SHALL handle all execution contexts with optional parameters for customization.

#### Scenario: setup_logging() works in all contexts

Given `setup_logging()` is called
When the function executes
Then it configures:
  1. Console handler (with level parameter, colorized)
  2. File handler (always DEBUG level, rotation enabled)
  3. Prefect handler (if in Prefect context, optional via enable_prefect=True)
And all handlers are active and functional
And the returned logger is ready to use immediately

#### Scenario: Optional enable_prefect parameter

Given `setup_logging(enable_prefect=False)` is called
When the function executes
Then Prefect handler initialization is skipped
And console + file handlers are still configured
And other code can disable Prefect integration if needed

#### Scenario: Configurable log levels and file paths

Given `setup_logging(level="DEBUG", log_file="custom.log")`
When the function executes
Then the console handler uses the specified level
And file logs are written to the specified path
And existing callers with default parameters continue to work

### Requirement: Backward Compatibility

All existing code SHALL continue to work without modifications.

#### Scenario: Existing flow.py code works unchanged

Given existing code: `logger = setup_logging(level="INFO", log_file="gratis_torrent.log")`
When the new logging system is implemented
Then the code continues to work
And no changes to `flow.py` are required
And logs appear in both console and Prefect (when applicable)

#### Scenario: Logger calls in tasks require no changes

Given loguru calls like `logger.info("message")` in task functions
When the task runs in Prefect
Then the message automatically appears in Prefect's task log
And the task code does not need to import or use Prefect's logger directly

### Requirement: Error Resilience

The logging system SHALL NOT cause task failures due to logging errors.

#### Scenario: Prefect logger failure does not crash task

Given Prefect handler encounters an error (e.g., network issue)
When `prefect_logger.info()` raises an exception
Then the exception is caught and silently ignored
And the task continues executing
And logs still appear in console and file (fallback handlers)

#### Scenario: Malformed messages don't crash logger

Given a message with special characters or encoding issues
When `prefect_handler()` attempts to format it
Then the handler processes it gracefully
And the message is delivered (possibly sanitized)
And execution continues

## MODIFIED Requirements

None - existing logging behavior is preserved and enhanced.

## REMOVED Requirements

None - no existing logging functionality is removed.

## Cross-References

- Related: Comprehensive test coverage (tests must verify logging works)
- Depends on: Python 3.11+ (already required by project)
- Integrates with: `scrapers/gratis_torrent/flow.py` (module using logging)
- Uses: `scrapers/utils/logging_config.py` (implementation module)

## Success Criteria

1. ✓ Loguru messages in Prefect tasks appear in task run logs with metadata
2. ✓ Graceful fallback when not in Prefect context (no errors)
3. ✓ All log levels are correctly mapped
4. ✓ Existing code requires no changes
5. ✓ Console and file logging continue to work
6. ✓ Unit tests pass with pytest-loguru plugin
7. ✓ Manual verification: Run flow locally and in Prefect, verify logs appear
