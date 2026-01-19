"""Unit tests for Prefect logging integration."""
# mypy: ignore-errors

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from scrapers.utils.logging_config import prefect_handler, setup_logging


class TestPrefectHandler:
    """Tests for prefect_handler sink function."""

    def test_handler_gracefully_fails_outside_prefect(self):
        """Test that handler does not raise error when not in Prefect context."""
        # Create a mock message record
        mock_message = MagicMock()
        mock_message.record = {
            "message": "Test message",
            "level": MagicMock(name="INFO"),
        }

        # Should not raise error when calling outside Prefect context
        try:
            prefect_handler(mock_message)
        except Exception as e:
            pytest.fail(
                f"prefect_handler should not raise exception outside Prefect context: {e}"
            )

    def test_handler_function_exists_and_callable(self):
        """Test that prefect_handler function exists and is callable."""
        assert callable(prefect_handler)
        assert prefect_handler.__name__ == "prefect_handler"

    def test_handler_has_docstring(self):
        """Test that prefect_handler has documentation."""
        assert prefect_handler.__doc__ is not None
        assert "Prefect" in prefect_handler.__doc__


class TestSetupLogging:
    """Tests for setup_logging context detection and handler setup."""

    def test_setup_logging_initializes_without_error(self, tmp_path):
        """Test that setup_logging() can be called without errors."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(level="INFO", log_file=str(log_file))
        assert logger is not None

    def test_setup_logging_outside_prefect_context(self, tmp_path, capsys):
        """Test that setup_logging() works correctly outside Prefect context."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(
            level="INFO", log_file=str(log_file), enable_prefect=True
        )

        # Should succeed without errors
        logger.info("Test message")

        # Verify message appears in console
        captured = capsys.readouterr()
        assert "Test message" in captured.out

    def test_setup_logging_with_enable_prefect_false(self, tmp_path, capsys):
        """Test that Prefect handler is skipped when enable_prefect=False."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(
            level="INFO", log_file=str(log_file), enable_prefect=False
        )

        # Should have console and file handlers (2 total)
        num_handlers = len(logger._core.handlers)

        # Note: 2 handlers for console + file (no prefect handler)
        assert num_handlers == 2

    def test_setup_logging_with_enable_prefect_true(self, tmp_path):
        """Test that Prefect handler is added when enable_prefect=True."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(
            level="INFO", log_file=str(log_file), enable_prefect=True
        )

        # Check that we have 3 handlers (console, file, prefect)
        num_handlers = len(logger._core.handlers)

        # Should have 3 handlers (console, file, prefect handler)
        assert num_handlers == 3

    def test_setup_logging_creates_file(self, tmp_path, capsys):
        """Test that setup_logging() creates the log file."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(level="INFO", log_file=str(log_file))

        logger.info("Test message to file")

        # Wait for file to be written
        import time

        time.sleep(0.1)

        # Verify file was created
        assert log_file.exists()

        # Verify message is in file
        content = log_file.read_text()
        assert "Test message to file" in content

    def test_setup_logging_default_parameters(self, tmp_path, capsys):
        """Test that setup_logging() works with default parameters."""
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            logger = setup_logging()

            logger.info("Test with defaults")

            # Should have created scraper.log in current directory
            assert Path(tmp_path / "scraper.log").exists()
        finally:
            os.chdir(original_cwd)

    def test_setup_logging_console_level_respected(self, tmp_path, capsys):
        """Test that console log level is respected."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(level="WARNING", log_file=str(log_file))

        logger.debug("Debug message")
        logger.warning("Warning message")

        captured = capsys.readouterr()

        # Debug should not appear (level is WARNING)
        assert "Debug message" not in captured.out
        # Warning should appear
        assert "Warning message" in captured.out

    def test_setup_logging_file_always_debug(self, tmp_path):
        """Test that file handler always captures DEBUG level."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(level="WARNING", log_file=str(log_file))

        logger.debug("Debug message for file")

        import time

        time.sleep(0.1)

        content = log_file.read_text()
        # File should have debug message even though console level is WARNING
        assert "Debug message for file" in content


class TestBackwardCompatibility:
    """Tests for backward compatibility with existing code."""

    def test_flow_module_imports(self):
        """Test that flow.py still imports successfully."""
        from scrapers.gratis_torrent import flow

        assert flow is not None

    def test_existing_flow_logger_call(self):
        """Test that existing logger calls still work."""
        from scrapers.gratis_torrent.flow import logger

        # Should not raise any errors
        logger.info("Test message from flow")
        logger.warning("Test warning from flow")
        logger.error("Test error from flow")

    def test_setup_logging_backward_compatible_signature(self, tmp_path):
        """Test that setup_logging() can be called with old signature."""
        log_file = tmp_path / "test.log"

        # Old call style (without enable_prefect)
        logger = setup_logging(level="INFO", log_file=str(log_file))

        assert logger is not None
        logger.info("Old style call")
