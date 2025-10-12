"""BigQuery client for data operations."""

import json
import warnings

from google.cloud import bigquery
from loguru import logger

from .config import Config

# Suppress quota project warning for user credentials
warnings.filterwarnings("ignore", message=".*quota project.*")


def get_client() -> bigquery.Client:
    """
    Create and return BigQuery client.

    Returns:
        Configured BigQuery client
    """
    return bigquery.Client(project=Config.GCP_PROJECT_ID)


def load_schema() -> list[bigquery.SchemaField]:
    """
    Load BigQuery table schema from schema.json file.

    Returns:
        List of BigQuery SchemaField objects

    Raises:
        FileNotFoundError: If schema file is not found
    """
    if not Config.SCHEMA_FILE.exists():
        raise FileNotFoundError(f"Schema file not found at {Config.SCHEMA_FILE}")

    with open(Config.SCHEMA_FILE, "r") as f:
        schema = json.load(f)

    logger.info(f"Schema loaded from {Config.SCHEMA_FILE}")
    return schema


def create_dataset(client: bigquery.Client) -> None:
    """
    Create BigQuery dataset if it doesn't exist.

    Args:
        client: BigQuery client instance
    """
    dataset_id = f"{Config.GCP_PROJECT_ID}.{Config.DATASET_ID}"
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = Config.LOCATION

    client.create_dataset(dataset, exists_ok=True)
    logger.info(f"Dataset {dataset_id} ready")


def delete_table(client: bigquery.Client, table_name: str) -> None:
    """
    Delete a BigQuery table if it exists.

    Args:
        client: BigQuery client instance
        table_name: Name of the table to delete
    """
    table_id = Config.get_full_table_id(table_name)
    client.delete_table(table_id, not_found_ok=True)
    logger.info(f"Table {table_id} deleted")


def create_table(client: bigquery.Client, table_name: str, force_recreate: bool = False) -> None:
    """
    Create BigQuery table if it doesn't exist.

    Args:
        client: BigQuery client instance
        table_name: Name of the table to create
        force_recreate: If True, delete and recreate the table
    """
    table_id = Config.get_full_table_id(table_name)
    schema = load_schema()

    if force_recreate:
        delete_table(client, table_name)

    table = bigquery.Table(table_id, schema=schema)
    client.create_table(table, exists_ok=True)
    logger.info(f"Table {table_id} ready")


def load_data_to_staging(client: bigquery.Client, data: list[dict]) -> None:
    """
    Load movie data into BigQuery staging table.

    Args:
        client: BigQuery client instance
        data: List of movie dictionaries to load
    """
    table_id = Config.get_full_table_id(Config.STAGING_TABLE_ID)
    table_ref = client.get_table(table_id)

    job_config = bigquery.LoadJobConfig(
        schema=load_schema(),
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    )

    logger.info(f"Loading {len(data)} movies to staging table")
    load_job = client.load_table_from_json(data, table_ref, job_config=job_config)
    load_job.result()

    logger.info("Data loaded to staging table successfully")


def merge_staging_to_main(client: bigquery.Client) -> int:
    """
    Merge data from staging table to main table.

    Args:
        client: BigQuery client instance

    Returns:
        Number of rows affected
    """
    target_table = Config.get_full_table_id(Config.TABLE_ID)
    source_table = Config.get_full_table_id(Config.STAGING_TABLE_ID)

    merge_statement = f"""
    MERGE INTO `{target_table}` AS target
    USING `{source_table}` AS source
    ON target.link = source.link
    WHEN NOT MATCHED THEN
    INSERT (
        titulo_dublado,
        titulo_original,
        imdb,
        ano,
        genero,
        tamanho,
        duracao_minutos,
        qualidade_video,
        qualidade,
        dublado,
        sinopse,
        link
    )
    VALUES (
        source.titulo_dublado,
        source.titulo_original,
        source.imdb,
        source.ano,
        source.genero,
        source.tamanho,
        source.duracao_minutos,
        source.qualidade_video,
        source.qualidade,
        source.dublado,
        source.sinopse,
        source.link
    );
    """

    merge_query = client.query(merge_statement, location=Config.LOCATION)
    merge_query.result()

    rows_affected = merge_query.num_dml_affected_rows
    if rows_affected is None:
        rows_affected = 0
    logger.info(f"Merge completed: {rows_affected} rows affected")

    return rows_affected


def truncate_staging_table(client: bigquery.Client) -> None:
    """
    Truncate the staging table.

    Args:
        client: BigQuery client instance
    """
    staging_table = Config.get_full_table_id(Config.STAGING_TABLE_ID)

    truncate_query = f"TRUNCATE TABLE `{staging_table}`;"
    truncate_result = client.query(truncate_query, location=Config.LOCATION)
    truncate_result.result()

    logger.info("Staging table truncated successfully")


def setup_tables(client: bigquery.Client, recreate_staging: bool = True) -> None:
    """
    Setup all required tables (dataset, main table, staging table).

    Args:
        client: BigQuery client instance
        recreate_staging: If True, always recreate the staging table to ensure schema is up to date
    """
    create_dataset(client)
    create_table(client, Config.TABLE_ID)
    create_table(client, Config.STAGING_TABLE_ID, force_recreate=recreate_staging)


def load_movies_to_bigquery(movies: list[dict]) -> int:
    """
    Complete pipeline to load movies to BigQuery.

    Args:
        movies: List of movie dictionaries

    Returns:
        Number of rows merged into main table
    """
    client = get_client()

    # Setup tables
    setup_tables(client)

    # Load to staging
    load_data_to_staging(client, movies)

    # Merge to main
    rows_affected = merge_staging_to_main(client)

    # Clean up staging
    truncate_staging_table(client)

    return rows_affected
