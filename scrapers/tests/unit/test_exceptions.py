"""Tests for custom exceptions module."""

import pytest

from scrapers.utils.exceptions import (
    BigQueryException,
    FetchException,
    ParsingException,
    ScraperException,
    ValidationException,
)


class TestScraperException:
    """Test ScraperException base class."""

    def test_scraper_exception_instantiation(self):
        """Test ScraperException can be instantiated with message."""
        exc = ScraperException("Test error")
        assert str(exc) == "Test error"

    def test_scraper_exception_is_exception_subclass(self):
        """Test ScraperException is a subclass of Exception."""
        exc = ScraperException("Test")
        assert isinstance(exc, Exception)

    def test_scraper_exception_can_be_raised(self):
        """Test ScraperException can be raised and caught."""
        with pytest.raises(ScraperException) as exc_info:
            raise ScraperException("Custom error message")
        assert str(exc_info.value) == "Custom error message"

    def test_scraper_exception_no_args(self):
        """Test ScraperException can be raised without arguments."""
        with pytest.raises(ScraperException):
            raise ScraperException()

    def test_scraper_exception_multiple_args(self):
        """Test ScraperException with multiple arguments."""
        exc = ScraperException("Error", "Details", 123)
        assert "Error" in str(exc)


class TestParsingException:
    """Test ParsingException class."""

    def test_parsing_exception_instantiation(self):
        """Test ParsingException can be instantiated."""
        exc = ParsingException("Failed to parse HTML")
        assert str(exc) == "Failed to parse HTML"

    def test_parsing_exception_is_scraper_exception(self):
        """Test ParsingException is subclass of ScraperException."""
        exc = ParsingException("Test")
        assert isinstance(exc, ScraperException)
        assert isinstance(exc, Exception)

    def test_parsing_exception_can_be_raised_and_caught_as_scraper(self):
        """Test ParsingException can be caught as ScraperException."""
        with pytest.raises(ScraperException) as exc_info:
            raise ParsingException("Parse error")
        assert isinstance(exc_info.value, ParsingException)

    def test_parsing_exception_specific_catch(self):
        """Test ParsingException can be caught specifically."""
        with pytest.raises(ParsingException):
            raise ParsingException("Specific parse error")


class TestValidationException:
    """Test ValidationException class."""

    def test_validation_exception_instantiation(self):
        """Test ValidationException can be instantiated."""
        exc = ValidationException("Invalid movie data")
        assert str(exc) == "Invalid movie data"

    def test_validation_exception_is_scraper_exception(self):
        """Test ValidationException is subclass of ScraperException."""
        exc = ValidationException("Test")
        assert isinstance(exc, ScraperException)
        assert isinstance(exc, Exception)

    def test_validation_exception_can_be_raised_and_caught_as_scraper(self):
        """Test ValidationException can be caught as ScraperException."""
        with pytest.raises(ScraperException) as exc_info:
            raise ValidationException("Validation failed")
        assert isinstance(exc_info.value, ValidationException)

    def test_validation_exception_specific_catch(self):
        """Test ValidationException can be caught specifically."""
        with pytest.raises(ValidationException):
            raise ValidationException("IMDB rating out of range")


class TestFetchException:
    """Test FetchException class."""

    def test_fetch_exception_instantiation(self):
        """Test FetchException can be instantiated."""
        exc = FetchException("HTTP 404 Not Found")
        assert str(exc) == "HTTP 404 Not Found"

    def test_fetch_exception_is_scraper_exception(self):
        """Test FetchException is subclass of ScraperException."""
        exc = FetchException("Test")
        assert isinstance(exc, ScraperException)
        assert isinstance(exc, Exception)

    def test_fetch_exception_can_be_raised_and_caught_as_scraper(self):
        """Test FetchException can be caught as ScraperException."""
        with pytest.raises(ScraperException) as exc_info:
            raise FetchException("Connection timeout")
        assert isinstance(exc_info.value, FetchException)

    def test_fetch_exception_specific_catch(self):
        """Test FetchException can be caught specifically."""
        with pytest.raises(FetchException):
            raise FetchException("Network error")

    def test_fetch_exception_with_http_status_code(self):
        """Test FetchException with HTTP status code information."""
        exc = FetchException("HTTP 500: Internal Server Error")
        assert "500" in str(exc)


class TestBigQueryException:
    """Test BigQueryException class."""

    def test_bigquery_exception_instantiation(self):
        """Test BigQueryException can be instantiated."""
        exc = BigQueryException("Failed to load data")
        assert str(exc) == "Failed to load data"

    def test_bigquery_exception_is_scraper_exception(self):
        """Test BigQueryException is subclass of ScraperException."""
        exc = BigQueryException("Test")
        assert isinstance(exc, ScraperException)
        assert isinstance(exc, Exception)

    def test_bigquery_exception_can_be_raised_and_caught_as_scraper(self):
        """Test BigQueryException can be caught as ScraperException."""
        with pytest.raises(ScraperException) as exc_info:
            raise BigQueryException("BigQuery timeout")
        assert isinstance(exc_info.value, BigQueryException)

    def test_bigquery_exception_specific_catch(self):
        """Test BigQueryException can be caught specifically."""
        with pytest.raises(BigQueryException):
            raise BigQueryException("Schema mismatch")


class TestExceptionHierarchy:
    """Test exception hierarchy and inheritance."""

    def test_all_custom_exceptions_inherit_from_scraper_exception(self):
        """Test all custom exceptions inherit from ScraperException."""
        exceptions = [
            ParsingException("test"),
            ValidationException("test"),
            FetchException("test"),
            BigQueryException("test"),
        ]
        for exc in exceptions:
            assert isinstance(exc, ScraperException)

    def test_exception_catching_order(self):
        """Test exception catching order works correctly."""
        # More specific exception should be caught first
        try:
            raise FetchException("Network error")
        except FetchException:
            caught = True
        except ScraperException:
            caught = False
        assert caught is True

    def test_generic_scraper_exception_catches_all(self):
        """Test generic ScraperException catches all subclasses."""
        specific_exceptions = [
            ParsingException("Parse"),
            ValidationException("Validation"),
            FetchException("Fetch"),
            BigQueryException("BigQuery"),
        ]

        for exc in specific_exceptions:
            try:
                raise exc
            except ScraperException as e:
                assert isinstance(e, ScraperException)
            else:
                pytest.fail(f"Expected ScraperException to catch {type(exc)}")

    def test_exception_message_preservation(self):
        """Test that exception messages are preserved through catching."""
        test_message = "Detailed error: Something went wrong"

        try:
            raise ParsingException(test_message)
        except ScraperException as e:
            assert str(e) == test_message


class TestExceptionAttributes:
    """Test exception attributes and methods."""

    def test_exception_args_attribute(self):
        """Test exception args attribute."""
        exc = ScraperException("Arg1", "Arg2")
        assert len(exc.args) == 2
        assert exc.args[0] == "Arg1"
        assert exc.args[1] == "Arg2"

    def test_exception_string_representation(self):
        """Test exception string representation."""
        exc = ScraperException("Test exception")
        assert repr(exc).startswith("ScraperException")
        assert str(exc) == "Test exception"

    def test_exception_with_cause(self):
        """Test exception with __cause__ (exception chaining)."""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise FetchException("Failed to fetch") from e
        except FetchException as e:
            assert e.__cause__ is not None
            assert isinstance(e.__cause__, ValueError)
