"""Utility script to recreate BigQuery tables with updated schema."""

import sys
from pathlib import Path

# Add parent directory to path so we can import src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scrapers.gratis_torrent.bigquery_client import create_table, delete_table, get_client
from src.scrapers.gratis_torrent.config import Config
from loguru import logger


def recreate_all_tables():
    """Recreate all BigQuery tables with the current schema."""
    client = get_client()

    logger.info("Recreating BigQuery tables with updated schema...")

    # Recreate staging table
    logger.info(f"Recreating staging table: {Config.STAGING_TABLE_ID}")
    delete_table(client, Config.STAGING_TABLE_ID)
    create_table(client, Config.STAGING_TABLE_ID)

    # Recreate main table (WARNING: This will delete existing data!)
    logger.warning(f"Recreating main table: {Config.TABLE_ID} - This will DELETE existing data!")
    response = input("Are you sure you want to recreate the main table? (yes/no): ")

    if response.lower() == "yes":
        delete_table(client, Config.TABLE_ID)
        create_table(client, Config.TABLE_ID)
        logger.info("Main table recreated successfully")
    else:
        logger.info("Skipping main table recreation")

    logger.info("Tables setup completed!")


if __name__ == "__main__":
    recreate_all_tables()
