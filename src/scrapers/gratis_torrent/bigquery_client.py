"""BigQuery client for data operations."""

import json
import warnings
from datetime import datetime

from google.cloud import bigquery
from loguru import logger

from scrapers.gratis_torrent.config import Config

# Suppress quota project warning for user credentials
warnings.filterwarnings("ignore", message=".*quota project.*")


def _json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


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

    except Exception as e:
        if "Not found: Table" in str(e):
            table_reference = bigquery.Table(table_id, schema=schema)
            client.create_table(table_reference)
            logger.info(f"Table {table_id} created with new schema")
        else:
            logger.error(f"Error creating or updating table {table_id}: {e}")
            raise


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

    # Convert datetime objects to ISO 8601 strings for JSON serialization
    serialized_data = json.loads(json.dumps(data, default=_json_serial))

    logger.info(f"Loading {len(serialized_data)} movies to staging table")
    load_job = client.load_table_from_json(
        serialized_data, table_ref, job_config=job_config
    )
    load_job.result()

    logger.success("Data loaded to staging table successfully")


def merge_staging_to_main(client: bigquery.Client) -> int:
    """
    Merge data from staging table to main table. Following the schema defined in the SCHEMA_FILE in Config object.

    Args:
        client: BigQuery client instance

    Returns:
        Number of rows affected
    """
    target_table = Config.get_full_table_id(Config.TABLE_ID)
    source_table = Config.get_full_table_id(Config.STAGING_TABLE_ID)
    schema = json.loads(Config.SCHEMA_FILE.read_text())

    columns = [col_obj.name for col_obj in schema]
    merge_statement = f"""
    merge into `{target_table}` as target
    using `{source_table}` as source
    on target.link = source.link
    when matched then
    update set
        {",".join(f"target.{col}=source.{col}" for col in columns if col != "date_updated")},
        target.date_updated = CURRENT_TIMESTAMP()
    WHEN NOT MATCHED THEN
    INSERT (
        {columns}
    )
    VALUES (
        {",".join(f"source.{col}" for col in columns if col != "date_updated")},
        CURRENT_TIMESTAMP()
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
