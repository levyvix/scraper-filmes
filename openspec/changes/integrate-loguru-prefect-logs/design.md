# Design: Loguru + Prefect Logging Integration

## Problem Statement

Loguru is configured to output to console and file, but when running inside Prefect tasks, these logs don't appear in Prefect's task run logs. The issue is that:

1. **Loguru bypasses Python's logging module** - it writes directly to stderr
2. **Prefect's `get_run_logger()`** expects Python logging calls or explicit logger usage
3. **`log_prints=True`** captures stdout/stderr but loses structure and metadata
4. **No task context** in logs - difficult to correlate logs with specific runs in Prefect Cloud

## Solution Overview

Create a custom loguru **sink** that routes messages to Prefect's `get_run_logger()` when available, with graceful fallback to console/file when not in Prefect context.

### Architecture

```
┌─────────────────────────────────────────────────────┐
│ Logger Call (anywhere in code)                      │
│ logger.info("message"), logger.warning(), etc.      │
└──────────────────┬──────────────────────────────────┘
                   │
                   ↓
        ┌──────────────────────┐
        │ setup_logging()      │
        │ (logging_config.py)  │
        └──────────┬───────────┘
                   │
        ┌──────────┴─────────────────┐
        │                            │
        ↓ In Prefect?               ↓ No
    ┌──────────────────┐      ┌────────────────┐
    │ Setup Prefect    │      │ Standard Setup │
    │ Handler (sink)   │      │ Console + File │
    │ File (backup)    │      └────────────────┘
    └──────────────────┘


Prefect Handler:
├─ Call get_run_logger()
├─ Format message
├─ Pass to Prefect logger
└─ Prefect logger adds metadata:
   ├─ Task name
   ├─ Run ID
   ├─ Timestamp
   └─ Log level
```

## Implementation Details

### 1. Prefect Handler Function

Location: `scrapers/utils/logging_config.py`

```python
def prefect_handler(message):
    """Loguru sink for Prefect integration."""
    try:
        from prefect import get_run_logger

        # We're in Prefect context - use its logger
        prefect_logger = get_run_logger()
        record = message.record
        level_name = record['level'].name.lower()

        # Map loguru levels to logging methods
        if level_name == 'debug':
            prefect_logger.debug(record['message'])
        elif level_name == 'info':
            prefect_logger.info(record['message'])
        elif level_name == 'warning':
            prefect_logger.warning(record['message'])
        elif level_name == 'error':
            prefect_logger.error(record['message'])
        elif level_name == 'critical':
            prefect_logger.critical(record['message'])
        else:
            prefect_logger.info(record['message'])
    except RuntimeError:
        # Not in Prefect context - fall through to other handlers
        pass
```

### 2. Updated setup_logging()

```python
def setup_logging(level: str = "INFO", log_file: str = "scraper.log",
                  enable_prefect: bool = True):
    """
    Configure logging with Prefect integration support.

    Args:
        level: Console log level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file
        enable_prefect: When True, route logs to Prefect when available
    """
    from loguru import logger

    # Always remove default handler
    logger.remove()

    # Add console handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=level,
        colorize=True,
    )

    # Add file handler (always captures DEBUG+)
    log_path = Path(log_file)
    logger.add(
        log_path,
        rotation="10 MB",
        retention="1 week",
        compression="zip",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    )

    # Add Prefect handler if enabled
    if enable_prefect:
        logger.add(
            prefect_handler,
            format="{message}",
            level="DEBUG",
        )

    logger.info(f"Logging configured - Console: {level}, File: {log_path}")
    return logger
```

### 3. Context Detection Strategy

**Option A: Try/Except (Recommended)**
- Simple and reliable
- Catch `RuntimeError` from `get_run_logger()` when not in Prefect
- No external dependencies

**Option B: Explicit Flag**
- Require env variable like `PREFECT_DEPLOYMENT_ID`
- More predictable but requires setup
- Better for containerized environments

**Decision**: Use **Option A** (Try/Except) - simpler, works everywhere.

## Execution Flow

### Scenario 1: Local Script (no Prefect)

```
1. Import flow.py
   ├─ setup_logging() called
   │  ├─ Add console handler ✓
   │  ├─ Add file handler ✓
   │  ├─ Try to add prefect_handler
   │  │  ├─ get_run_logger() → RuntimeError
   │  │  └─ Skip prefect_handler ✓
   │  └─ Logger ready
   └─ Logs go to console + file.log

2. logger.info("Starting scraper")
   ├─ Console output: "... INFO | ... Starting scraper"
   ├─ File output: same
   └─ Prefect handler skipped (no context)
```

### Scenario 2: Prefect Task Execution

```
1. Prefect starts task execution
   ├─ Initializes Prefect context
   └─ Prefect's event handler active

2. Task code imports logger
   ├─ setup_logging() called
   │  ├─ Add console handler ✓
   │  ├─ Add file handler ✓
   │  ├─ Try to add prefect_handler
   │  │  ├─ get_run_logger() → success
   │  │  └─ Prefect handler added ✓
   │  └─ Logger ready (3 handlers)
   └─ Logs go to console + file + Prefect

3. logger.info("Scraped 100 movies")
   ├─ Console: "... INFO | ... Scraped 100 movies"
   ├─ File: same
   ├─ Prefect handler:
   │  ├─ Extract message via prefect_handler()
   │  ├─ Call prefect_logger.info(message)
   │  └─ Prefect adds metadata (task_name, run_id, etc.)
   └─ Message appears in Prefect Cloud UI
```

### Scenario 3: Unit Tests

```
1. pytest starts
   ├─ No Prefect context
   └─ setup_logging() adds console + file handlers

2. Test imports logger (same code path)
   ├─ Prefect handler tries to initialize
   ├─ get_run_logger() → RuntimeError
   └─ Skipped gracefully ✓

3. logger.info() in test
   ├─ Console captures via capsys or pytest-loguru
   ├─ File logs captured
   └─ Test assertions pass
```

## Handler Details

### Message Format Handling

Loguru's `record` object contains:
- `message.record['message']` - the formatted message string
- `message.record['level'].name` - 'DEBUG', 'INFO', etc.
- `message.record['name']` - module name
- `message.record['function']` - function name
- `message.record['line']` - line number

Prefect's logger expects standard Python logging calls (debug, info, warning, error, critical).

### Log Level Mapping

| Loguru | Python | Prefect |
|--------|--------|---------|
| DEBUG  | DEBUG  | debug() |
| INFO   | INFO   | info()  |
| WARNING| WARNING| warning()|
| ERROR  | ERROR  | error() |
| CRITICAL| CRITICAL | critical() |

### Error Handling

1. **Not in Prefect context**: RuntimeError from `get_run_logger()`
   - Caught silently
   - Other handlers continue to work
   - Result: logs go to console/file but not Prefect (expected)

2. **Prefect logger fails**: Exception in prefect_logger.info()
   - Caught and ignored (fail-safe design)
   - Result: logs still go to console/file

3. **Message serialization fails**: Exception in formatter
   - Re-raised by loguru
   - Caught at task level, logged as task failure
   - Result: visible error in Prefect UI

## Integration Points

### Module: `flow.py`
- Line 17: `logger = setup_logging(level="INFO", log_file="gratis_torrent.log")`
- No changes needed - works with new signature
- Logger automatically supports Prefect when running in tasks

### Module: `scraper.py`
- Existing logger calls work unchanged
- Logs automatically appear in Prefect when running as task

### Module: `bigquery_client.py`
- Existing logger calls work unchanged
- Logs automatically appear in Prefect when running as task

### Unit Tests
- Use `caplog` (pytest) to capture Python logging
- Use pytest-loguru plugin for loguru capture
- No Prefect context during tests (graceful degradation)

## Testing Strategy

### Unit Tests
1. Test context detection (Prefect vs. non-Prefect)
2. Test handler initialization
3. Test log level mapping
4. Test error handling (missing Prefect, failed logger)

### Integration Test
1. Run flow locally: `python -m scrapers.gratis_torrent.flow`
2. Verify logs appear in console
3. Verify logs appear in log file
4. (Manual) Run in Prefect Cloud and verify Prefect UI shows logs

### Edge Cases
- Very long log messages
- Special characters in log messages
- Multiple concurrent Prefect tasks
- Rapid logging (burst of messages)

## Dependencies

No new dependencies required:
- `loguru` - already installed
- `prefect` - already installed
- `prefect.get_run_logger()` - standard Prefect API

## Backwards Compatibility

✓ **Fully backwards compatible**
- Function signature extended with optional `enable_prefect=True`
- Existing callers work unchanged
- Graceful fallback when Prefect not available

## Known Limitations

1. **Prefect Cloud only**: Requires Prefect to be installed and context available
2. **Message format**: Prefect receives the final formatted message (can't extract raw args)
3. **Extra metadata**: Loguru-specific fields (exception info) may be lost

## Future Enhancements

1. Capture full loguru record and pass to Prefect with extra context
2. Support structured logging with JSON format
3. Integrate with Prefect Cloud's log aggregation
4. Add metrics/counters based on log levels

## References

- [Prefect Community Discussion: How do I save logs generated by loguru in imported modules?](https://linen.prefect.io/t/22667008/ulva73b9p-how-do-i-save-logs-generated-by-loguru-in-imported)
  - Discusses patterns for capturing loguru logs in Prefect contexts
  - Provides implementation guidance for handler routing

## Validation Plan

Run `openspec validate integrate-loguru-prefect-logs --strict` to ensure:
- All requirements have scenarios
- No dangling references
- Tasks are properly ordered
- Success criteria are testable
