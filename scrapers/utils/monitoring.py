"""Monitoring and alerting for scraper health checks."""

from datetime import datetime

from loguru import logger

from scrapers.utils.send_mail import send_email


class ScraperMonitor:
    """Monitor scraper health and send alerts for anomalies.

    This class tracks scraper execution and detects issues like:
    - Low movie counts (below threshold)
    - Failed loads (movies scraped but no rows loaded)
    - Poor load rates (high rejection rate)
    """

    def __init__(self, min_movies_threshold: int = 10) -> None:
        """Initialize the scraper monitor.

        Args:
            min_movies_threshold: Minimum number of movies expected to be scraped.
                                If below this, an alert is triggered.
        """
        self.min_movies_threshold = min_movies_threshold
        self.start_time = datetime.now()

    def check_results(self, movies_scraped: int, rows_loaded: int) -> bool:
        """Check if scraping results are healthy and alert if issues found.

        Args:
            movies_scraped: Total number of movies scraped
            rows_loaded: Number of rows successfully loaded to database

        Returns:
            True if results are healthy, False if issues detected
        """
        issues = []

        # Check for low movie count
        if movies_scraped < self.min_movies_threshold:
            issues.append(
                f"Low movie count: {movies_scraped} (expected >= {self.min_movies_threshold})"
            )

        # Check for load failures despite successful scraping
        if rows_loaded == 0 and movies_scraped > 0:
            issues.append(f"No rows loaded despite scraping {movies_scraped} movies")

        # Check for poor load rate (high rejection/validation failure rate)
        load_rate = rows_loaded / movies_scraped if movies_scraped > 0 else 0
        if load_rate < 0.5:
            issues.append(f"Low load rate: {load_rate:.1%}")

        if issues:
            self.send_alert(issues, movies_scraped, rows_loaded)
            return False

        logger.info(
            f"Scraper health check passed - {movies_scraped} movies, {rows_loaded} rows loaded"
        )
        return True

    def send_alert(
        self, issues: list[str], movies_scraped: int, rows_loaded: int
    ) -> None:
        """Send alert email about scraping issues.

        Args:
            issues: List of issue descriptions detected
            movies_scraped: Number of movies that were scraped
            rows_loaded: Number of rows that were successfully loaded
        """
        duration = (datetime.now() - self.start_time).total_seconds()

        subject = "🚨 Scraper Alert - Issues Detected"
        body = f"""
Scraper completed with issues:

Issues:
{chr(10).join(f"- {issue}" for issue in issues)}

Stats:
- Movies Scraped: {movies_scraped}
- Rows Loaded: {rows_loaded}
- Load Rate: {rows_loaded / movies_scraped * 100:.1f}% if movies_scraped > 0 else N/A
- Duration: {duration:.1f}s
- Timestamp: {datetime.now().isoformat()}
"""

        try:
            send_email(subject, body)
            logger.info("Alert email sent successfully")
        except Exception as e:
            logger.error(f"Failed to send alert email: {e}")
