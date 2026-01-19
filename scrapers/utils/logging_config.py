"""Centralized logging configuration for scrapers.

This module provides a unified logging setup using loguru that integrates
with Prefect's logging system when running within Prefect tasks.
"""

import sys
from pathlib import Path
from typing import Any


def prefect_handler(message: Any) -> None:
    """
    Loguru sink for Prefect task log integration.

    Routes loguru messages to Prefect's get_run_logger() when available.
    Gracefully degrades when not in Prefect context (RuntimeError is caught).

    Args:
        message: Loguru message record containing formatted message and metadata

    Note:
        This handler is designed to be used as a loguru sink. It extracts the
        log level from the message record and calls the appropriate method on
        Prefect's logger (debug, info, warning, error, critical).
    """
    try:
        from prefect import get_run_logger

        # We're in Prefect context - use its logger
        prefect_logger = get_run_logger()
        record = message.record
        level_name = record["level"].name.lower()

        # Map loguru levels to Python logging methods
        if level_name == "debug":
            prefect_logger.debug(record["message"])
        elif level_name == "info":
            prefect_logger.info(record["message"])
        elif level_name == "warning":
            prefect_logger.warning(record["message"])
        elif level_name == "error":
            prefect_logger.error(record["message"])
        elif level_name == "critical":
            prefect_logger.critical(record["message"])
        else:
            prefect_logger.info(record["message"])
    except RuntimeError:
        # Not in Prefect context - other handlers will capture the message
        pass


def setup_logging(
    level: str = "INFO", log_file: str = "scraper.log", enable_prefect: bool = True
) -> Any:
    """
    Configure logging with console and file handlers, with optional Prefect integration.

    Args:
        level: Log level for console output (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file (supports rotation)
        enable_prefect: When True, route logs to Prefect when available (default: True)

    Returns:
        Configured logger instance

    Note:
        When running within Prefect tasks, loguru logs are routed to Prefect's
        get_run_logger() for integration with Prefect's task run logs. When not
        in a Prefect context, logs fall back to console and file handlers.

        Prefect handler detection is automatic and graceful - if Prefect is not
        available or not in a task context, an error is caught silently and
        logging continues with console and file handlers.
    """
    from loguru import logger

    # Remove default handler
    logger.remove()

    # Console handler with colored output
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=level,
        colorize=True,
    )

    # File handler with rotation
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
