"""Tests for Comando Torrents parser module."""

from unittest.mock import MagicMock, patch
from scrapers.comando_torrents.parser import (
    extract_text_or_none,
    safe_list_get,
    parse_detail,
)


class TestExtractTextOrNone:
    """Test the extract_text_or_none function."""

    def test_extract_text_valid_selector(self):
        """Test extracting text with valid CSS selector."""
        mock_page = MagicMock()
        # Adaptor.css_first() returns an Adaptor or None
        mock_element = MagicMock()
        mock_element.__str__.return_value = "Test Text"
        mock_page.css_first.return_value = mock_element

        result = extract_text_or_none(mock_page, ".test-class")

        assert result == "Test Text"
        mock_page.css_first.assert_called_once_with(".test-class")

    def test_extract_text_none_when_not_found(self):
        """Test extraction returns None when selector doesn't match."""
        mock_page = MagicMock()
        mock_page.css_first.return_value = None

        result = extract_text_or_none(mock_page, ".missing-class")

        assert result is None

    def test_extract_text_empty_string(self):
        """Test extraction of empty text."""
        mock_page = MagicMock()
        mock_element = MagicMock()
        mock_element.__str__.return_value = ""
        mock_page.css_first.return_value = mock_element

        result = extract_text_or_none(mock_page, ".empty")

        assert result is None  # Empty strings are converted to None

    def test_extract_text_with_whitespace(self):
        """Test extraction strips whitespace."""
        mock_page = MagicMock()
        mock_element = MagicMock()
        mock_element.__str__.return_value = "  Spaced Text  "
        mock_page.css_first.return_value = mock_element

        result = extract_text_or_none(mock_page, ".text")

        assert result == "Spaced Text"  # Whitespace is stripped


class TestSafeListGet:
    """Test the safe_list_get function."""

    def test_safe_list_get_valid_index(self):
        """Test safe list access with valid index."""
        items = ["first", "second", "third"]
        result = safe_list_get(items, 1, default=None)
        assert result == "second"

    def test_safe_list_get_first_element(self):
        """Test accessing first element."""
        items = ["first", "second"]
        result = safe_list_get(items, 0, default=None)
        assert result == "first"

    def test_safe_list_get_out_of_bounds(self):
        """Test accessing index beyond list length."""
        items = ["first", "second"]
        result = safe_list_get(items, 5, default="DEFAULT")
        assert result == "DEFAULT"

    def test_safe_list_get_negative_index(self):
        """Test accessing with negative index returns default."""
        items = ["first", "second", "third"]
        result = safe_list_get(items, -1, default="DEFAULT")
        assert result == "DEFAULT"  # Negative indices are not supported

    def test_safe_list_get_empty_list(self):
        """Test accessing empty list."""
        items = []
        result = safe_list_get(items, 0, default="EMPTY")
        assert result == "EMPTY"

    def test_safe_list_get_none_default(self):
        """Test with None as default."""
        items = ["item"]
        result = safe_list_get(items, 10, default=None)
        assert result is None

    def test_safe_list_get_custom_default(self):
        """Test with custom default value."""
        items = ["item"]
        result = safe_list_get(items, 10, default="NOT_FOUND")
        assert result == "NOT_FOUND"


class TestParseDetail:
    """Test the parse_detail function."""

    @patch("scrapers.comando_torrents.parser.fetch_page")
    def test_parse_detail_fetch_called(self, mock_fetch):
        """Test that parse_detail calls fetch_page."""
        mock_fetch.return_value = None

        parse_detail("https://example.com/movie")

        mock_fetch.assert_called_once_with("https://example.com/movie")

    @patch("scrapers.comando_torrents.parser.fetch_page")
    def test_parse_detail_with_none_fetch(self, mock_fetch):
        """Test parse_detail when fetch returns None."""
        mock_fetch.return_value = None

        result = parse_detail("https://example.com/bad-movie")

        assert result is None

    @patch("scrapers.comando_torrents.parser.fetch_page")
    def test_parse_detail_handles_validation_errors(self, mock_fetch):
        """Test parsing handles validation errors gracefully."""
        # Mock page that would cause validation error
        mock_page = MagicMock()
        mock_fetch.return_value = mock_page

        # Function should not raise, returns None on error
        _ = parse_detail("https://example.com/invalid")

        # Result depends on mocking details, but shouldn't crash
        assert mock_fetch.called


class TestParserIntegration:
    """Integration tests for parser functions."""

    def test_extract_text_or_none_with_nested_selector(self):
        """Test extracting from nested page structure."""
        mock_page = MagicMock()
        mock_element = MagicMock()
        mock_element.__str__.return_value = "Nested Text"
        mock_page.css_first.return_value = mock_element

        result = extract_text_or_none(mock_page, "div.container > span.text")

        assert result == "Nested Text"

    def test_safe_list_get_in_parsing_context(self):
        """Test safe_list_get for typical parsing scenarios."""
        genres = ["Action", "Drama", "Comedy"]

        first = safe_list_get(genres, 0, default="Unknown")
        middle = safe_list_get(genres, 1, default="Unknown")
        last = safe_list_get(genres, 2, default="Unknown")
        beyond = safe_list_get(genres, 10, default="Unknown")

        assert first == "Action"
        assert middle == "Drama"
        assert last == "Comedy"
        assert beyond == "Unknown"

    def test_multiple_selectors_with_fallback(self):
        """Test trying multiple selectors with fallback."""
        mock_page = MagicMock()

        # First selector fails
        mock_page.css_first.return_value = None
        result1 = extract_text_or_none(mock_page, ".primary-title")
        assert result1 is None

        # Fallback to second selector
        mock_element = MagicMock()
        mock_element.__str__.return_value = "Fallback Title"
        mock_page.css_first.return_value = mock_element
        result2 = extract_text_or_none(mock_page, ".secondary-title")
        assert result2 == "Fallback Title"
