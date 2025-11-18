"""Centralized logging configuration for scrapers.

This module provides a unified logging setup using loguru that integrates
with Prefect's logging system when running within Prefect tasks.
"""

from loguru import logger, Logger
import sys
from pathlib import Path


def setup_logging(level: str = "INFO", log_file: str = "scraper.log") -> Logger:
    """
    Configure logging with console and file handlers.

    Args:
        level: Log level for console output (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file (supports rotation)

    Returns:
        Configured logger instance

    Note:
        When running within Prefect tasks with log_prints=True, loguru logs
        will be captured by Prefect's logging system automatically.
    """
    # Remove default handler
    logger.remove()

    # Console handler with colored output
    logger.add(
        sys.stderr,
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

    logger.info(f"Logging configured - Console: {level}, File: {log_path}")
    return logger
