import os
import sys
from pathlib import Path

import pandas as pd
from prefect import flow, task
from sqlalchemy import create_engine

from src.database.insert_to_database import create_and_insert

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


@task(
    name="Run GratisTorrent Scraper",
    log_prints=True,
    retries=3,
    retry_delay_seconds=10,
)
def run_gratis_scraper():
    """Execute the GratisTorrent scraper and generate movies_gratis.json"""
    json_path = "src/scrapers/gratis_torrent/movies_gratis.json"

    # Delete previous file if it exists
    if os.path.exists(json_path):
        os.remove(json_path)
        print(f"Previous {json_path} deleted")

    # Run the scraper
    result = os.system("uv run src/scrapers/gratis_torrent/extract.py")

    if result != 0:
        error_message = f"Scraper failed with exit code {result}. Please check the scraper logs for details."
        raise RuntimeError(error_message)

    # Check if file was created in expected location
    if os.path.exists(json_path):
        print("GratisTorrent scraper completed successfully")
        return

    # Check if file was created in current directory
    if os.path.exists("movies_gratis.json"):
        print("JSON file found in current directory, moving to gratis_torrent/")
        os.rename("movies_gratis.json", json_path)
        print("GratisTorrent scraper completed successfully")
        return

    # If we get here, file was not created
    error_message = f"Expected JSON file not found at {json_path} or in current directory. The scraper may have failed silently."
    raise FileNotFoundError(error_message)


@task(
    name="Insert into database",
    log_prints=True,
    retries=3,
    retry_delay_seconds=10,
)
def insert_movies(path: str, engine):
    """Insert scraped movies into SQLite database"""
    create_and_insert(path, engine)
    print(f"Movies from {path} inserted into database")


@task(
    name="Export to BigQuery",
    log_prints=True,
)
def export_to_bigquery():
    """Optional: Export data to BigQuery"""
    result = os.system("uv run src/scrapers/gratis_torrent/send_to_bq.py")

    if result == 0:
        print("Data exported to BigQuery successfully")
        return

    error_message = f"BigQuery export failed with exit code {result}. Check the BigQuery logs for details."
    print(error_message)


@task(
    name="Get Movie Stats",
    log_prints=True,
)
def get_stats(engine):
    """Print statistics about scraped movies"""
    df = pd.read_sql_query(
        """
        SELECT COUNT(*) as total_movies,
               (SELECT COUNT(DISTINCT genre) FROM genres) as total_genres,
               AVG(imdb) as avg_imdb,
               MAX(date_updated) as latest_update
        FROM movies
        """,
        engine,
    )

    print("=" * 50)
    print("MOVIE DATABASE STATISTICS")
    print("=" * 50)
    print(df.to_string(index=False))
    print("=" * 50)

    return df


@flow(name="GratisTorrent Flow", log_prints=True)
def gratis_torrent_flow(export_bq: bool = False):
    """
    Main Prefect flow for GratisTorrent scraping pipeline

    Args:
        export_bq: If True, exports data to BigQuery after database insertion
    """
    # Create SQLite engine
    engine = create_engine("sqlite:///dbs/movie_database.db")

    # Task 1: Run the scraper
    run_gratis_scraper()

    # Task 2: Insert into database
    insert_movies("src/scrapers/gratis_torrent/movies_gratis.json", engine)

    # Task 3: Get statistics
    get_stats(engine)

    # Task 4 (Optional): Export to BigQuery
    if export_bq:
        export_to_bigquery()

    print("GratisTorrent flow completed successfully!")


if __name__ == "__main__":
    gratis_torrent_flow(export_bq=True)
