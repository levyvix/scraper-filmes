# Specification: Shared Utilities Test Coverage

## Overview

Complete test coverage for shared utilities (data_quality, send_mail, exceptions), bringing coverage from 0%-100% (varies) to ≥85% across all modules. Tests validate data validation, email notifications, and exception handling.

## ADDED Requirements

### Requirement: Data Quality Validation Coverage
Tests SHALL cover all validation methods in DataQualityChecker for valid and invalid data. The data_quality module has 18% coverage and MUST reach ≥85% coverage. Tests MUST verify all validation rules and edge cases.

#### Scenario: Validate movie with all fields in valid range
Given Movie object with:
- IMDB rating: 7.5 (0-10 valid)
- Year: 2020 (≥1888 valid)
- All other fields populated
- When `DataQualityChecker.check_movie(movie)` is called
- Then validation passes (returns True)
- And no warnings logged

#### Scenario: Reject movie with IMDB out of range
Given Movie with IMDB rating 11.5 (invalid, >10):
- When `check_movie()` is called
- Then validation fails (returns False)
- And warning logged specifying "IMDB out of range"
- And validation details are available (which field, why)

#### Scenario: Reject movie with invalid year
Given Movie with year 1500 (invalid, <1888):
- When `check_movie()` is called
- Then validation fails (returns False)
- And warning specifies year is too old
- And movie is not accepted

#### Scenario: Validate movie with None fields
Given Movie with several None fields (optional data):
- When `check_movie()` is called
- Then validation considers None as acceptable (partial data)
- And returns True if other validations pass
- And does not fail on missing optional fields

#### Scenario: Validate borderline values
Given Movie with IMDB=0 and IMDB=10 (boundaries):
- When `check_movie()` is called
- Then both are valid
- And year=1888 is valid (lowest allowed)
- And year=current_year is valid

#### Scenario: Detect missing required fields
Given Movie missing titulo_dublado (required):
- When `check_movie()` is called
- Then validation fails
- And error indicates missing required field
- And validation is clear about requirement

#### Scenario: Validate genre field
Given Movie with genre containing invalid characters or format:
- When `check_movie()` validates genre
- Then genre validation rules are applied
- And results are consistent with parser behavior
- And genre can be None (optional)

#### Scenario: Check multiple validation failures
Given Movie with IMDB=15 AND year=1000 AND missing titulo:
- When `check_movie()` is called
- Then returns False
- And all failures are reported (or first failure with context)
- And caller knows why validation failed

### Requirement: Email Notification Coverage
Tests SHALL cover email sending and error handling for the SendMail module. The send_mail module has 0% coverage and MUST reach ≥80% coverage. Tests MUST verify SMTP operations and error scenarios.

#### Scenario: Send email successfully
Given email configuration and recipient list:
- When `send_email(to, subject, body)` is called
- Then SMTP connection is established
- And message is formatted correctly
- And email is sent without exception
- And success is logged

#### Scenario: Send email with SMTP configuration
Given SMTP server address, port, credentials:
- When email is sent
- Then SMTP server is used (address and port are correct)
- And credentials are applied (if required)
- And connection is closed properly

#### Scenario: Handle SMTP connection failure
Given unreachable SMTP server:
- When `send_email()` is called
- Then SMTPException is raised or logged
- And error message is clear
- And caller can retry or use fallback

#### Scenario: Send email with HTML body
Given HTML-formatted email body:
- When `send_email()` is called
- Then MIME type is set correctly (text/html)
- And HTML is rendered properly
- And special characters are encoded

#### Scenario: Send email with multiple recipients
Given recipient list with 5 addresses:
- When `send_email(to_list, subject, body)` is called
- Then all recipients receive email
- And no recipient is skipped
- And success is verified

#### Scenario: Handle invalid email address
Given invalid recipient address (missing @):
- When `send_email()` is called
- Then validation catches invalid format
- And error is raised or logged
- And other recipients (if any) are not affected

### Requirement: Exception Hierarchy Coverage
Tests SHALL cover the exception hierarchy to ensure all exception types are testable and properly defined. The exceptions module has 100% coverage and MUST maintain this level. Tests MUST verify exception instantiation and catching behavior.

#### Scenario: Raise FetchException
Given network error with original exception:
- When `FetchException(message, original_error)` is raised
- Then exception is catchable
- And message and original error are accessible
- And traceback is preserved for debugging

#### Scenario: Raise ScraperException
Given scraper failure:
- When `ScraperException(message)` is raised
- Then exception is caught by `except ScraperException`
- And not caught by generic `Exception` handler (if code expects it)
- And message is informative

#### Scenario: Raise SchemaException
Given BigQuery schema mismatch:
- When `SchemaException(message)` is raised
- Then exception identifies schema issue
- And caller can respond appropriately
- And not confused with other exceptions

#### Scenario: Exception types are distinct
Given multiple exception types:
- When exceptions are raised
- Then `isinstance(exc, FetchException)` works correctly
- And exception hierarchy is as designed
- And no exception type shadows another

## MODIFIED Requirements

### Requirement: Test Infrastructure
Test infrastructure SHALL be enhanced with fixtures and utilities for shared module testing. Fixtures MUST provide standard test data and mock objects for consistent testing.

#### Scenario: Use test Movie fixtures
Given standard test Movie objects:
- When tests create valid/invalid Movies
- Then fixtures provide consistent data
- And tests don't need to construct complex objects
- And edge cases are pre-defined

#### Scenario: Mock SMTP server
Given tests for email functionality:
- When tests run
- Then SMTP is mocked (not hitting real server)
- And mock verifies correct calls were made
- And email content is verifiable without sending

## REMOVED Requirements

(None; this is additive specification)

## Coverage Targets

| Module | Current | Target | Lines to Add |
|--------|---------|--------|--------------|
| utils/data_quality.py | 18% | 85% | 35+ tests |
| utils/send_mail.py | 0% | 80% | 20+ tests |
| utils/exceptions.py | 100% | 100% | 0 (maintain) |

## Test Files

- `scrapers/tests/unit/test_data_quality.py` (new, enhance existing)
- `scrapers/tests/unit/test_send_mail.py` (new)
- `scrapers/tests/unit/test_exceptions.py` (new, if not exists)

## Dependencies

- smtplib (built-in, use unittest.mock)
- unittest.mock.patch for SMTP mocking

## Notes

- SMTP mocking can use `unittest.mock.patch('smtplib.SMTP')`
- DataQualityChecker validation logic should match Pydantic model rules
- Ensure tests handle edge cases (None values, boundary values, empty strings)
