"""BigQuery client for data operations."""

import json
import warnings
from typing import Any

from google.cloud import bigquery
from google.cloud.exceptions import GoogleCloudError
from loguru import logger

from scrapers.gratis_torrent.config import Config
from scrapers.gratis_torrent.models import Movie
from scrapers.utils.exceptions import BigQueryException

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
        raise FileNotFoundError(
            f"Schema file not found at {Config.PROJECT_ROOT}/{Config.SCHEMA_FILE}"
        )

    schema_raw = json.loads(Config.SCHEMA_FILE.read_text("utf-8"))
    schema = [
        bigquery.SchemaField(
            name=field["name"],
            field_type=field["type"],
            mode=field["mode"],
        )
        for field in schema_raw
    ]

    logger.info(f"Schema loaded from {Config.PROJECT_ROOT}/{Config.SCHEMA_FILE}")
    return schema


def create_dataset(client: bigquery.Client) -> None:
    """
    Create BigQuery dataset if it doesn't exist.

    Args:
        client: BigQuery client instance

    Raises:
        BigQueryException: If dataset creation fails
    """
    dataset_id = f"{Config.GCP_PROJECT_ID}.{Config.DATASET_ID}"
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = Config.LOCATION

    try:
        client.create_dataset(dataset, exists_ok=True)
        logger.info(f"Dataset {dataset_id} ready")
    except GoogleCloudError as e:
        logger.error(f"Failed to create dataset {dataset_id}: {e}")
        raise BigQueryException(f"Failed to create dataset {dataset_id}") from e
    except Exception as e:
        logger.error(f"Unexpected error creating dataset {dataset_id}: {e}")
        raise BigQueryException(
            f"Unexpected error creating dataset {dataset_id}"
        ) from e


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


def create_table(
    client: bigquery.Client, table_name: str, force_recreate: bool = False
) -> None:
    """
    Create BigQuery table if it doesn't exist.

    Args:
        client: BigQuery client instance
        table_name: Name of the table to create
        force_recreate: If True, delete and recreate the table
    """
    table_id = Config.get_full_table_id(table_name)
    schema: list[bigquery.SchemaField] = load_schema()

    if force_recreate:
        delete_table(client, table_name)
        table_reference = bigquery.Table(table_id, schema=schema)
        client.create_table(table_reference)
        logger.info(f"Table {table_id} recreated with new schema")
        return

    try:
        table = client.get_table(table_id)
        current_schema_fields = {field.name: field for field in table.schema}
        new_schema_fields = {field.name: field for field in schema}

        fields_to_add = []
        for field_name, field_definition in new_schema_fields.items():
            if field_name not in current_schema_fields:
                fields_to_add.append(
                    bigquery.SchemaField(
                        name=field_definition.name,
                        field_type=str(field_definition.field_type),
                        mode=str(field_definition.mode),
                    )
                )

        if fields_to_add:
            updated_schema = table.schema + fields_to_add
            table.schema = updated_schema
            client.update_table(table, ["schema"])
            logger.info(
                f"Added new columns to table {table_id}: {[f.name for f in fields_to_add]}"
            )
        else:
            logger.info(f"Table {table_id} already exists and schema is up to date.")

    except GoogleCloudError as e:
        if "Not found: Table" in str(e):
            try:
                table_reference = bigquery.Table(table_id, schema=schema)
                client.create_table(table_reference)
                logger.info(f"Table {table_id} created with new schema")
            except GoogleCloudError as create_error:
                logger.error(f"Failed to create table {table_id}: {create_error}")
                raise BigQueryException(
                    f"Failed to create table {table_id}"
                ) from create_error
        else:
            logger.error(f"Error creating or updating table {table_id}: {e}")
            raise BigQueryException(
                f"Failed to create or update table {table_id}"
            ) from e
    except Exception as e:
        logger.error(f"Unexpected error with table {table_id}: {e}")
        raise BigQueryException(f"Unexpected error with table {table_id}") from e


def load_data_to_staging(client: bigquery.Client, data: list[dict[str, Any]]) -> int:
    """
    Load movie data into BigQuery staging table.

    Args:
        client: BigQuery client instance
        data: List of movie dictionaries to load

    Returns:
        Number of rows loaded

    Raises:
        BigQueryException: If load fails
    """
    if not data:
        logger.warning("No data to load to staging")
        return 0

    table_id = Config.get_full_table_id(Config.STAGING_TABLE_ID)

    try:
        table_ref = client.get_table(table_id)

        job_config = bigquery.LoadJobConfig(
            schema=load_schema(),
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        )

        logger.info(f"Loading {len(data)} rows to {table_id}")
        load_job = client.load_table_from_json(data, table_ref, job_config=job_config)

        # Wait for job to complete with timeout
        result = load_job.result(timeout=300)  # 5 minute timeout

        if load_job.errors:
            logger.error(f"Load job had errors: {load_job.errors}")
            raise BigQueryException(f"Load failed with errors: {load_job.errors}")

        rows_loaded = int(result.output_rows) if result.output_rows else 0
        logger.info(f"Successfully loaded {rows_loaded} rows to staging")
        return rows_loaded

    except GoogleCloudError as e:
        logger.error(f"BigQuery error loading to staging: {e}")
        raise BigQueryException(f"Failed to load to staging: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error loading to staging: {e}")
        raise BigQueryException(f"Unexpected load failure: {e}") from e


def merge_staging_to_main(client: bigquery.Client) -> int:
    """
    Merge data from staging table to main table.

    Args:
        client: BigQuery client instance

    Returns:
        Number of rows affected

    Raises:
        BigQueryException: If merge fails
    """
    target_table = Config.get_full_table_id(Config.TABLE_ID)
    source_table = Config.get_full_table_id(Config.STAGING_TABLE_ID)

    merge_statement = f"""
    MERGE INTO `{target_table}` AS target
    USING `{source_table}` AS source
    ON target.link = source.link
    WHEN MATCHED THEN
    UPDATE SET
        target.titulo_dublado = source.titulo_dublado,
        target.titulo_original = source.titulo_original,
        target.imdb = source.imdb,
        target.ano = source.ano,
        target.genero = source.genero,
        target.tamanho = source.tamanho,
        target.duracao_minutos = source.duracao_minutos,
        target.qualidade_video = source.qualidade_video,
        target.qualidade = source.qualidade,
        target.dublado = source.dublado,
        target.sinopse = source.sinopse,
        target.poster_url = source.poster_url,
        target.date_updated = CURRENT_TIMESTAMP()
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
        link,
        poster_url,
        date_updated
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
        source.link,
        source.poster_url,
        CURRENT_TIMESTAMP()
    );
    """

    try:
        logger.info(f"Merging data from {source_table} to {target_table}")
        merge_query = client.query(merge_statement, location=Config.LOCATION)

        # Wait for query to complete with timeout
        merge_query.result(timeout=300)  # 5 minute timeout

        rows_affected = merge_query.num_dml_affected_rows or 0
        logger.info(f"Merge completed: {rows_affected} rows affected")

        return rows_affected

    except GoogleCloudError as e:
        logger.error(f"BigQuery error during merge: {e}")
        raise BigQueryException(f"Failed to merge staging to main: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error during merge: {e}")
        raise BigQueryException(f"Unexpected merge failure: {e}") from e


def truncate_staging_table(client: bigquery.Client) -> None:
    """
    Truncate the staging table.

    Args:
        client: BigQuery client instance

    Raises:
        BigQueryException: If truncate fails
    """
    staging_table = Config.get_full_table_id(Config.STAGING_TABLE_ID)

    try:
        logger.info(f"Truncating staging table {staging_table}")
        truncate_query = f"TRUNCATE TABLE `{staging_table}`;"
        truncate_result = client.query(truncate_query, location=Config.LOCATION)

        # Wait for query to complete with timeout
        truncate_result.result(timeout=300)  # 5 minute timeout

        logger.info("Staging table truncated successfully")

    except GoogleCloudError as e:
        logger.error(f"BigQuery error truncating staging table: {e}")
        raise BigQueryException(f"Failed to truncate staging table: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error truncating staging table: {e}")
        raise BigQueryException(f"Unexpected truncate failure: {e}") from e


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


def movies_to_dict(movies: list[Movie]) -> list[dict[str, Any]]:
    return list(map(Movie.model_dump, movies))


def load_movies_to_bigquery(movies: list[Movie]) -> int:
    """
    Complete pipeline to load movies to BigQuery.

    Args:
        movies: List of movie dictionaries

    Returns:
        int: Number of rows merged into main table
    """
    client = get_client()

    # Setup tables
    setup_tables(client)

    # Load to staging
    # unload movies to list of dicts
    movies_dict = movies_to_dict(movies)
    load_data_to_staging(client, movies_dict)

    # Merge to main
    rows_affected = merge_staging_to_main(client)

    # Clean up staging
    truncate_staging_table(client)

    return rows_affected
