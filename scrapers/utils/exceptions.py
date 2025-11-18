"""Custom exceptions for scraper operations."""


class ScraperException(Exception):
    """Base exception for scraper errors."""

    pass


class ParsingException(ScraperException):
    """Raised when parsing fails."""

    pass


class ValidationException(ScraperException):
    """Raised when data validation fails."""

    pass


class FetchException(ScraperException):
    """Raised when HTTP requests fail."""

    pass
