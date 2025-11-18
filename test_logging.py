#!/usr/bin/env python3
"""Quick test script to verify logging configuration."""

from loguru import logger

# Test different log levels
logger.info("Testing INFO level logging")
logger.warning("Testing WARNING level logging")
logger.error("Testing ERROR level logging")
logger.success("Testing SUCCESS level logging")
logger.debug("Testing DEBUG level logging (may not show in console)")

print("✓ Logging test complete - check output above")
