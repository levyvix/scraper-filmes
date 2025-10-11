"""
Simple DAG to run the GratisTorrent scraper pipeline:
1. Extract movies from website
2. Send data to BigQuery
"""

from extract import main as extract
from send_to_bq import main as send_to_bq


def run_dag():
    """Run the complete scraper pipeline."""
    extract()
    send_to_bq()


if __name__ == "__main__":
    run_dag()
