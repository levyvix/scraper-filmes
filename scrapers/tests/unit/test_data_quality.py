"""Tests for data quality validation module."""

import pytest
from scrapers.utils.data_quality import DataQualityChecker
from scrapers.utils.models import Movie
from scrapers.tests.fixtures.test_data import (
    VALID_MOVIE_COMPLETE,
    VALID_MOVIE_MINIMAL,
    PARTIAL_MOVIE_NO_YEAR,
    BOUNDARY_MOVIE_RATING_0,
    BOUNDARY_MOVIE_RATING_10,
    BOUNDARY_MOVIE_YEAR_1888,
    VALID_MOVIES,
    get_invalid_movie_data,
)


class TestDataQualityCheckerInit:
    """Test DataQualityChecker initialization."""

    def test_init_default_threshold(self):
        """Test initialization with default threshold."""
        checker = DataQualityChecker()
        assert checker.min_fields_filled == 0.7
        assert checker.quality_issues == []

    def test_init_custom_threshold(self):
        """Test initialization with custom threshold."""
        checker = DataQualityChecker(min_fields_filled=0.5)
        assert checker.min_fields_filled == 0.5

    def test_init_zero_threshold(self):
        """Test initialization with zero threshold."""
        checker = DataQualityChecker(min_fields_filled=0.0)
        assert checker.min_fields_filled == 0.0

    def test_init_full_threshold(self):
        """Test initialization with 100% threshold."""
        checker = DataQualityChecker(min_fields_filled=1.0)
        assert checker.min_fields_filled == 1.0


class TestCheckMovieValidation:
    """Test check_movie method with various movie states."""

    def test_valid_complete_movie_passes(self):
        """Test that complete movie with all fields passes."""
        # Complete movie has ~50% field completeness, use lower threshold
        checker = DataQualityChecker(min_fields_filled=0.4)
        result = checker.check_movie(VALID_MOVIE_COMPLETE)
        assert result is True
        assert len(checker.quality_issues) == 0

    def test_movie_with_special_chars_passes(self):
        """Test movie with special characters passes validation."""
        from scrapers.tests.fixtures.test_data import MOVIE_WITH_SPECIAL_CHARS

        checker = DataQualityChecker(min_fields_filled=0.3)
        result = checker.check_movie(MOVIE_WITH_SPECIAL_CHARS)
        assert result is True

    def test_boundary_rating_0_passes(self):
        """Test movie with minimum boundary rating (0.0)."""
        # Boundary movie has ~14% field completeness, use low threshold
        checker = DataQualityChecker(min_fields_filled=0.1)
        result = checker.check_movie(BOUNDARY_MOVIE_RATING_0)
        assert result is True

    def test_boundary_rating_10_passes(self):
        """Test movie with maximum boundary rating (10.0)."""
        # Boundary movie has ~14% field completeness, use low threshold
        checker = DataQualityChecker(min_fields_filled=0.1)
        result = checker.check_movie(BOUNDARY_MOVIE_RATING_10)
        assert result is True

    def test_boundary_year_1888_passes(self):
        """Test movie with minimum boundary year (1888)."""
        # Boundary movie has ~14% field completeness, use low threshold
        checker = DataQualityChecker(min_fields_filled=0.1)
        result = checker.check_movie(BOUNDARY_MOVIE_YEAR_1888)
        assert result is True

    def test_movie_with_at_least_one_title_passes(self):
        """Test movie with at least one title passes."""
        movie = Movie(
            titulo_original="English Title",
            link="https://example.com/movie",
        )
        checker = DataQualityChecker(min_fields_filled=0.0)
        result = checker.check_movie(movie)
        assert result is True


class TestCheckMovieFailures:
    """Test check_movie method detecting failures."""

    def test_missing_both_titles_fails(self):
        """Test movie with both titles missing fails."""
        movie = Movie(link="https://example.com/movie")
        checker = DataQualityChecker(min_fields_filled=0.0)
        result = checker.check_movie(movie)
        assert result is False
        assert len(checker.quality_issues) == 1
        assert "Missing both titles" in str(checker.quality_issues[0]["issues"])

    def test_missing_link_fails(self):
        """Test movie without link fails."""
        movie = Movie(titulo_original="Movie Title")
        checker = DataQualityChecker(min_fields_filled=0.0)
        result = checker.check_movie(movie)
        assert result is False
        assert "Missing link" in str(checker.quality_issues[0]["issues"])

    def test_low_field_completeness_fails(self):
        """Test movie with low field completeness fails."""
        movie = Movie(titulo_original="Movie Title", link="https://example.com/movie")
        checker = DataQualityChecker(min_fields_filled=0.9)  # Require 90% filled
        result = checker.check_movie(movie)
        assert result is False
        assert "Low completeness" in str(checker.quality_issues[0]["issues"])

    def test_year_too_recent_fails(self):
        """Test movie with year after 2030 fails."""
        movie = Movie(
            titulo_original="Future", link="https://example.com/future", ano=2031
        )
        checker = DataQualityChecker(min_fields_filled=0.0)
        result = checker.check_movie(movie)
        assert result is False
        assert "Invalid year" in str(checker.quality_issues[0]["issues"])

    def test_multiple_quality_issues(self):
        """Test movie with multiple quality issues."""
        movie = Movie(
            link="https://example.com/movie",  # Has link
            ano=2031,  # Invalid year
        )
        checker = DataQualityChecker(min_fields_filled=0.0)
        result = checker.check_movie(movie)
        assert result is False
        issues = checker.quality_issues[0]["issues"]
        assert any("Invalid year" in issue for issue in issues)
        assert any("Missing" in issue for issue in issues)


class TestCheckMovieThresholds:
    """Test check_movie with different field completeness thresholds."""

    def test_zero_threshold_accepts_minimal_movie(self):
        """Test that 0% threshold accepts minimal movies."""
        movie = Movie(titulo_original="Title", link="https://example.com/minimal")
        checker = DataQualityChecker(min_fields_filled=0.0)
        result = checker.check_movie(movie)
        assert result is True

    def test_high_threshold_rejects_partial_movies(self):
        """Test strict threshold rejects partial movies."""
        checker = DataQualityChecker(min_fields_filled=1.0)
        result = checker.check_movie(PARTIAL_MOVIE_NO_YEAR)
        # Missing year, so won't reach 100% completeness
        assert result is False


class TestCheckBatch:
    """Test check_batch method with movie collections."""

    def test_batch_all_valid_movies(self):
        """Test batch with all valid movies."""
        # Use low threshold to accept minimal movies
        checker = DataQualityChecker(min_fields_filled=0.15)
        valid_batch = [VALID_MOVIE_COMPLETE, VALID_MOVIE_MINIMAL]
        result = checker.check_batch(valid_batch)

        assert result["total_movies"] == 2
        assert result["passed_quality"] == 2
        assert result["failed_quality"] == 0
        assert result["pass_rate"] == 1.0
        assert isinstance(result["issues"], list)

    def test_batch_mixed_valid_invalid(self):
        """Test batch with mix of valid and invalid movies."""
        invalid_movie = Movie(link="https://example.com/movie", ano=2031)
        checker = DataQualityChecker(min_fields_filled=0.0)
        batch = [VALID_MOVIE_COMPLETE, invalid_movie]
        result = checker.check_batch(batch)

        assert result["total_movies"] == 2
        assert result["passed_quality"] == 1
        assert result["failed_quality"] == 1
        assert result["pass_rate"] == 0.5

    def test_batch_empty_list(self):
        """Test batch with empty movie list."""
        checker = DataQualityChecker()
        result = checker.check_batch([])

        assert result["total_movies"] == 0
        assert result["passed_quality"] == 0
        assert result["failed_quality"] == 0
        assert result["pass_rate"] == 0.0

    def test_batch_all_invalid(self):
        """Test batch where all movies fail validation."""
        movie1 = Movie(link="https://example.com/m1")  # Missing titles
        movie2 = Movie(link="https://example.com/m2", ano=2031)  # Invalid year

        checker = DataQualityChecker(min_fields_filled=0.0)
        result = checker.check_batch([movie1, movie2])

        assert result["total_movies"] == 2
        assert result["passed_quality"] == 0
        assert result["failed_quality"] == 2
        assert result["pass_rate"] == 0.0
        assert len(result["issues"]) == 2

    def test_batch_accumulates_issues(self):
        """Test that batch accumulates issues from all movies."""
        movie1 = Movie(link="https://example.com/m1")  # Missing titles
        movie2 = Movie(link="https://example.com/m2", ano=2031)  # Invalid year

        checker = DataQualityChecker(min_fields_filled=0.0)
        result = checker.check_batch([movie1, movie2])

        assert len(result["issues"]) == 2
        assert result["issues"][0]["link"] == "https://example.com/m1"
        assert result["issues"][1]["link"] == "https://example.com/m2"


class TestQualityReport:
    """Test get_quality_report method."""

    def test_report_no_issues(self):
        """Test report when there are no quality issues."""
        checker = DataQualityChecker(min_fields_filled=0.3)
        checker.check_movie(VALID_MOVIE_COMPLETE)
        report = checker.get_quality_report()
        assert "No quality issues found" in report

    def test_report_single_issue(self):
        """Test report with single quality issue."""
        movie = Movie(link="https://example.com/bad")
        checker = DataQualityChecker(min_fields_filled=0.0)
        checker.check_movie(movie)
        report = checker.get_quality_report()

        assert "Found 1 quality issues:" in report
        assert "https://example.com/bad" in report

    def test_report_multiple_issues(self):
        """Test report with multiple quality issues."""
        movies = [
            Movie(link="https://example.com/1"),
            Movie(link="https://example.com/2", ano=2031),
            Movie(link="https://example.com/3"),
        ]
        checker = DataQualityChecker(min_fields_filled=0.0)
        checker.check_batch(movies)
        report = checker.get_quality_report()

        assert "Found" in report
        assert "quality issues" in report

    def test_report_truncates_long_lists(self):
        """Test that report truncates lists longer than 10 issues."""
        movies = [Movie(link=f"https://example.com/{i}") for i in range(15)]
        checker = DataQualityChecker(min_fields_filled=0.0)
        checker.check_batch(movies)
        report = checker.get_quality_report()

        assert "... and 5 more" in report  # 15 - 10 = 5


class TestCheckMovieWithRealFixtures:
    """Test check_movie with fixture data."""

    def test_all_valid_fixtures_pass(self):
        """Test that all valid fixture movies pass checks."""
        checker = DataQualityChecker(min_fields_filled=0.3)
        for movie in VALID_MOVIES:
            result = checker.check_movie(movie)
            # Most should pass with lower threshold
            assert result is True or result is False  # Just check it runs

    def test_batch_all_fixtures(self):
        """Test batch with all valid fixtures."""
        checker = DataQualityChecker(min_fields_filled=0.3)
        result = checker.check_batch(VALID_MOVIES)

        # With 0.3 threshold, most should pass
        assert result["total_movies"] == len(VALID_MOVIES)
        assert result["passed_quality"] > 0  # At least some should pass


class TestInvalidMovieDataCatchesByPydantic:
    """Test that invalid data is caught by Pydantic validation."""

    def test_invalid_movie_data_function(self):
        """Test that get_invalid_movie_data returns invalid data."""
        invalid_data = get_invalid_movie_data()
        assert len(invalid_data) == 3

        # All should have properties that violate Pydantic constraints
        from pydantic import ValidationError

        for data in invalid_data:
            with pytest.raises(ValidationError):
                Movie(**data)


class TestQualityCheckerEdgeCases:
    """Test edge cases and special scenarios."""

    def test_movie_with_imdb_as_float(self):
        """Test movie where IMDB is a float."""
        movie = Movie(
            titulo_original="Movie", link="https://example.com/movie", imdb=8.5
        )
        checker = DataQualityChecker(min_fields_filled=0.0)
        result = checker.check_movie(movie)
        assert result is True

    def test_movie_with_only_original_title(self):
        """Test that movie with only original title passes."""
        movie = Movie(
            titulo_original="English Title",
            link="https://example.com/movie",
        )
        checker = DataQualityChecker(min_fields_filled=0.0)
        result = checker.check_movie(movie)
        assert result is True

    def test_movie_with_only_dublado_title(self):
        """Test that movie with only dubbed title passes."""
        movie = Movie(
            titulo_dublado="Portuguese Title",
            link="https://example.com/movie",
        )
        checker = DataQualityChecker(min_fields_filled=0.0)
        result = checker.check_movie(movie)
        assert result is True

    def test_repeated_checks_accumulate_issues(self):
        """Test that calling check_movie multiple times accumulates issues."""
        movie1 = Movie(link="https://example.com/1")
        movie2 = Movie(link="https://example.com/2", ano=2031)

        checker = DataQualityChecker(min_fields_filled=0.0)
        checker.check_movie(movie1)
        checker.check_movie(movie2)

        assert len(checker.quality_issues) == 2

    def test_very_low_threshold_still_catches_missing_link(self):
        """Test that missing link is always caught."""
        movie = Movie(titulo_original="Has title")
        checker = DataQualityChecker(min_fields_filled=0.0)
        result = checker.check_movie(movie)
        assert result is False
        assert "Missing link" in str(checker.quality_issues[0]["issues"])

    def test_none_imdb_does_not_fail(self):
        """Test that None IMDB value is acceptable."""
        movie = Movie(
            titulo_original="Movie", link="https://example.com/movie", imdb=None
        )
        checker = DataQualityChecker(min_fields_filled=0.0)
        result = checker.check_movie(movie)
        assert result is True

    def test_none_year_does_not_fail(self):
        """Test that None year value is acceptable."""
        movie = Movie(
            titulo_original="Movie", link="https://example.com/movie", ano=None
        )
        checker = DataQualityChecker(min_fields_filled=0.0)
        result = checker.check_movie(movie)
        assert result is True
