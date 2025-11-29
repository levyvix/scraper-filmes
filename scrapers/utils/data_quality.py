"""Data quality validation for scraped movies."""

from typing import Any, Sequence
from loguru import logger
from scrapers.utils.models import Movie


class DataQualityChecker:
    """Validate scraped data quality."""

    def __init__(self, min_fields_filled: float = 0.7):
        """
        Initialize the data quality checker.

        Args:
            min_fields_filled: Minimum proportion of fields that should be filled (0.0-1.0)
        """
        self.min_fields_filled = min_fields_filled
        self.quality_issues: list[dict[str, Any]] = []

    def check_movie(self, movie: Movie) -> bool:
        """
        Check if a movie meets quality standards.

        Args:
            movie: Movie object to validate

        Returns:
            True if movie passes quality checks, False otherwise
        """
        issues = []

        # Check required fields
        if not movie.titulo_dublado and not movie.titulo_original:
            issues.append("Missing both titles")

        if not movie.link:
            issues.append("Missing link")

        # Check field completeness
        total_fields = len(movie.model_fields)
        filled_fields = sum(
            1 for field, value in movie.model_dump().items() if value is not None
        )
        completeness = filled_fields / total_fields

        if completeness < self.min_fields_filled:
            issues.append(f"Low completeness: {completeness:.1%}")

        # Check data validity
        if movie.ano and (movie.ano < 1888 or movie.ano > 2030):
            issues.append(f"Invalid year: {movie.ano}")

        if movie.imdb:
            try:
                imdb_float = float(movie.imdb)
                if imdb_float < 0 or imdb_float > 10:
                    issues.append(f"Invalid IMDB: {movie.imdb}")
            except (ValueError, TypeError):
                issues.append(f"Invalid IMDB format: {movie.imdb}")

        if issues:
            self.quality_issues.append({"link": movie.link, "issues": issues})
            logger.warning(f"Quality issues for {movie.link}: {', '.join(issues)}")
            return False

        return True

    def check_batch(self, movies: Sequence[Movie]) -> dict[str, Any]:
        """
        Check quality of a batch of movies.

        Args:
            movies: List of Movie objects to validate

        Returns:
            Dictionary with quality metrics including:
            - total_movies: Total number of movies checked
            - passed_quality: Number of movies that passed
            - failed_quality: Number of movies that failed
            - pass_rate: Proportion of movies that passed (0.0-1.0)
            - issues: List of quality issues found
        """
        total = len(movies)
        passed = sum(1 for movie in movies if self.check_movie(movie))

        return {
            "total_movies": total,
            "passed_quality": passed,
            "failed_quality": total - passed,
            "pass_rate": passed / total if total > 0 else 0,
            "issues": self.quality_issues,
        }

    def get_quality_report(self) -> str:
        """
        Generate a human-readable quality report.

        Returns:
            Formatted string with quality statistics
        """
        if not self.quality_issues:
            return "No quality issues found"

        report_lines = [f"Found {len(self.quality_issues)} quality issues:"]
        for issue in self.quality_issues[:10]:  # Show first 10
            report_lines.append(f"  - {issue['link']}: {', '.join(issue['issues'])}")

        if len(self.quality_issues) > 10:
            report_lines.append(f"  ... and {len(self.quality_issues) - 10} more")

        return "\n".join(report_lines)
