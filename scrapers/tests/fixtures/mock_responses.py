"""Mock HTTP and API responses for testing."""

from unittest.mock import MagicMock
from bs4 import BeautifulSoup


# Mock response objects
class MockHTTPResponse:
    """Mock HTTP response for requests library."""

    def __init__(self, status_code: int = 200, text: str = ""):
        self.status_code = status_code
        self.text = text
        self.headers = {"Content-Type": "text/html"}

    def raise_for_status(self):
        """Raise exception if status code indicates error."""
        if 400 <= self.status_code < 600:
            from requests import HTTPError

            raise HTTPError(f"{self.status_code} error")


# Mock BeautifulSoup objects
EMPTY_SOUP = BeautifulSoup("<html></html>", "html.parser")

SOUP_WITH_MOVIE_LINKS = BeautifulSoup(
    """
    <html>
        <div id="capas_pequenas">
            <div><a href="http://example.com/movie1">Movie 1</a></div>
            <div><a href="http://example.com/movie2">Movie 2</a></div>
            <div><a href="http://example.com/movie3">Movie 3</a></div>
        </div>
    </html>
    """,
    "html.parser",
)

SOUP_WITH_DUPLICATE_LINKS = BeautifulSoup(
    """
    <html>
        <div id="capas_pequenas">
            <div><a href="http://example.com/movie1">Movie 1</a></div>
            <div><a href="http://example.com/movie1">Movie 1 Duplicate</a></div>
            <div><a href="http://example.com/movie2">Movie 2</a></div>
        </div>
    </html>
    """,
    "html.parser",
)

SOUP_NO_MOVIE_LINKS = BeautifulSoup(
    """
    <html>
        <body>No movies here</body>
    </html>
    """,
    "html.parser",
)


# BigQuery mock objects
class MockBigQueryClient:
    """Mock google.cloud.bigquery.Client."""

    def __init__(self):
        self.dataset_ref = None
        self.datasets = []
        self.tables = {}

    def list_datasets(self):
        """Return mock list of datasets."""
        return self.datasets

    def get_dataset(self, dataset_id):
        """Get mock dataset."""
        return MagicMock(dataset_id=dataset_id)

    def create_dataset(self, dataset):
        """Create mock dataset."""
        self.datasets.append(dataset)
        return dataset

    def get_table(self, table_id):
        """Get mock table."""
        return MagicMock(table_id=table_id)

    def load_table_from_json(self, json_rows, table_id, job_config=None):
        """Load JSON rows into mock table."""
        job = MagicMock()
        job.result = MagicMock(return_value=None)
        return job

    def query(self, query_str, job_config=None):
        """Execute mock query."""
        job = MagicMock()
        job.result = MagicMock(return_value=[])
        return job


class MockBigQueryJob:
    """Mock google.cloud.bigquery.LoadJob."""

    def __init__(self, total_rows=100):
        self.output_rows = total_rows
        self._done = False

    def result(self):
        """Wait for job completion."""
        self._done = True
        return self

    @property
    def done(self):
        """Check if job is done."""
        return self._done

    @property
    def output_rows(self):
        """Return number of output rows."""
        return self._output_rows

    @output_rows.setter
    def output_rows(self, value):
        self._output_rows = value


# Mock Prefect task results
class MockPrefectTaskResult:
    """Mock Prefect task execution result."""

    def __init__(self, data=None, error=None):
        self.data = data
        self.error = error
        self.status = "COMPLETED" if error is None else "FAILED"

    def get(self):
        """Get task result."""
        if self.error:
            raise self.error
        return self.data


# Mock HTML responses for parsers
MOCK_GRATIS_MOVIE_PAGE_COMPLETE = """
<html>
    <head><title>Inception - Gratis Torrent</title></head>
    <body>
        <h1>Inception</h1>
        <div class="movie-info">
            <span class="titulo-dublado">Origem</span>
            <span class="rating">8.8</span>
            <span class="ano">2010</span>
            <span class="genero">Sci-Fi, Action</span>
            <span class="downloads">5000</span>
            <a href="magnet:?xt=urn:btih:123456">Download Torrent</a>
        </div>
    </body>
</html>
"""

MOCK_GRATIS_MOVIE_PAGE_MINIMAL = """
<html>
    <head><title>Interstellar - Gratis Torrent</title></head>
    <body>
        <h1>Interstellar</h1>
        <div class="movie-info">
            <a href="magnet:?xt=urn:btih:789012">Download Torrent</a>
        </div>
    </body>
</html>
"""

MOCK_COMANDO_MOVIE_PAGE = """
<html>
    <body>
        <div class="movie-item">
            <h3>The Dark Knight</h3>
            <span class="rating">9.0</span>
            <span class="year">2008</span>
            <a href="http://example.com/dark-knight" class="movie-link">View</a>
            <span class="seeds">1000</span>
            <span class="peers">500</span>
        </div>
    </body>
</html>
"""
