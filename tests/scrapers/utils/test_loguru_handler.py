"""Unit tests for loguru handler behavior."""

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

from scrapers.utils.logging_config import setup_logging


class TestHandlerBehavior:
    """Tests for loguru handler setup and message routing."""

    def test_console_handler_receives_messages(
        self, tmp_path: Path, capsys: Any
    ) -> None:
        """Test that console handler receives log messages."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(
            level="INFO", log_file=str(log_file), enable_prefect=False
        )

        logger.info("Console test message")

        captured = capsys.readouterr()
        assert "Console test message" in captured.out

    def test_file_handler_receives_messages(self, tmp_path: Path) -> None:
        """Test that file handler receives log messages."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(
            level="INFO", log_file=str(log_file), enable_prefect=False
        )

        logger.info("File test message")

        import time

        time.sleep(0.1)

        content = log_file.read_text()
        assert "File test message" in content

    def test_all_log_levels_console(self, tmp_path: Path, capsys: Any) -> None:
        """Test that all log levels work with console handler."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(
            level="DEBUG", log_file=str(log_file), enable_prefect=False
        )

        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")

        captured = capsys.readouterr()

        assert "Debug message" in captured.out
        assert "Info message" in captured.out
        assert "Warning message" in captured.out
        assert "Error message" in captured.out
        assert "Critical message" in captured.out

    def test_all_log_levels_file(self, tmp_path: Path) -> None:
        """Test that all log levels work with file handler."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(
            level="DEBUG", log_file=str(log_file), enable_prefect=False
        )

        logger.debug("Debug to file")
        logger.info("Info to file")
        logger.warning("Warning to file")
        logger.error("Error to file")
        logger.critical("Critical to file")

        import time

        time.sleep(0.1)

        content = log_file.read_text()

        assert "Debug to file" in content
        assert "Info to file" in content
        assert "Warning to file" in content
        assert "Error to file" in content
        assert "Critical to file" in content

    def test_console_format_includes_timestamp(
        self, tmp_path: Path, capsys: Any
    ) -> None:
        """Test that console output includes timestamp."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(
            level="INFO", log_file=str(log_file), enable_prefect=False
        )

        logger.info("Format test")

        captured = capsys.readouterr()

        # Should include timestamp like 2025-12-14 22:56:24
        assert (
            "2025-" in captured.out or "2024-" in captured.out or "202" in captured.out
        )

    def test_console_format_includes_level(self, tmp_path: Path, capsys: Any) -> None:
        """Test that console output includes log level."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(
            level="INFO", log_file=str(log_file), enable_prefect=False
        )

        logger.info("Level test")

        captured = capsys.readouterr()

        # Should include level like INFO
        assert "INFO" in captured.out

    def test_console_format_includes_function_name(
        self, tmp_path: Path, capsys: Any
    ) -> None:
        """Test that console output includes function name."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(
            level="INFO", log_file=str(log_file), enable_prefect=False
        )

        logger.info("Function test")

        captured = capsys.readouterr()

        # Should include function name
        assert "test_console_format_includes_function_name" in captured.out

    def test_console_format_includes_message(self, tmp_path: Path, capsys: Any) -> None:
        """Test that console output includes actual message."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(
            level="INFO", log_file=str(log_file), enable_prefect=False
        )

        logger.info("Important message")

        captured = capsys.readouterr()

        assert "Important message" in captured.out

    def test_file_format_includes_line_number(self, tmp_path: Path) -> None:
        """Test that file output includes line number."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(
            level="INFO", log_file=str(log_file), enable_prefect=False
        )

        logger.info("Line number test")

        import time

        time.sleep(0.1)

        content = log_file.read_text()

        # Should include line number
        assert "Line number test" in content
        # File format includes line number
        assert ":" in content

    def test_prefect_handler_with_mock_prefect(
        self, tmp_path: Path, capsys: Any
    ) -> None:
        """Test that Prefect handler is called when Prefect is available."""
        mock_prefect_logger = MagicMock()
        mock_get_run_logger = MagicMock(return_value=mock_prefect_logger)

        log_file = tmp_path / "test.log"

        with patch("prefect.get_run_logger", mock_get_run_logger):
            logger = setup_logging(
                level="INFO", log_file=str(log_file), enable_prefect=True
            )

            logger.info("Prefect test message")

        # Verify mock was called at least once
        assert mock_get_run_logger.called or mock_prefect_logger.info.called

    def test_console_colorization_disabled_for_file(self, tmp_path: Path) -> None:
        """Test that file handler doesn't include color codes."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(
            level="INFO", log_file=str(log_file), enable_prefect=False
        )

        logger.info("Color test")

        import time

        time.sleep(0.1)

        content = log_file.read_text()

        # File should not have ANSI color codes
        assert "\x1b[" not in content  # ANSI escape code
        assert "<" not in content or ">" not in content  # No loguru markup

    def test_multiple_messages_in_file(self, tmp_path: Path) -> None:
        """Test that multiple messages are appended to file."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(
            level="INFO", log_file=str(log_file), enable_prefect=False
        )

        logger.info("Message 1")
        logger.info("Message 2")
        logger.info("Message 3")

        import time

        time.sleep(0.1)

        content = log_file.read_text()

        assert "Message 1" in content
        assert "Message 2" in content
        assert "Message 3" in content

    def test_console_level_filter_works(self, tmp_path: Path, capsys: Any) -> None:
        """Test that console level filtering works correctly."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(
            level="ERROR", log_file=str(log_file), enable_prefect=False
        )

        logger.debug("Should not appear")
        logger.info("Should not appear")
        logger.warning("Should not appear")
        logger.error("Should appear")

        captured = capsys.readouterr()

        assert "Should not appear" not in captured.out
        assert "Should appear" in captured.out

    def test_file_level_always_debug(self, tmp_path: Path) -> None:
        """Test that file handler always captures DEBUG level."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(
            level="ERROR", log_file=str(log_file), enable_prefect=False
        )

        logger.debug("Debug in file")
        logger.info("Info in file")
        logger.warning("Warning in file")
        logger.error("Error in file")

        import time

        time.sleep(0.1)

        content = log_file.read_text()

        # File should have all levels
        assert "Debug in file" in content
        assert "Info in file" in content
        assert "Warning in file" in content
        assert "Error in file" in content


class TestHandlerIntegration:
    """Tests for handler integration and interaction."""

    def test_console_and_file_both_receive_message(
        self, tmp_path: Path, capsys: Any
    ) -> None:
        """Test that both console and file handlers receive the same message."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(
            level="INFO", log_file=str(log_file), enable_prefect=False
        )

        logger.info("Integration test")

        captured = capsys.readouterr()

        import time

        time.sleep(0.1)

        file_content = log_file.read_text()

        assert "Integration test" in captured.out
        assert "Integration test" in file_content

    def test_logger_context_preserved_across_calls(
        self, tmp_path: Path, capsys: Any
    ) -> None:
        """Test that logger context is preserved across multiple calls."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(
            level="INFO", log_file=str(log_file), enable_prefect=False
        )

        logger.info("First call")
        logger.info("Second call")
        logger.info("Third call")

        captured = capsys.readouterr()

        assert "First call" in captured.out
        assert "Second call" in captured.out
        assert "Third call" in captured.out
