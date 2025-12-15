"""BigQuery client for data operations."""

import json
import os
import warnings
from typing import Any

import google.auth
import google.oauth2.service_account
from google.cloud import bigquery
from google.cloud.exceptions import GoogleCloudError

from scrapers.gratis_torrent.config import Config
from scrapers.utils.exceptions import BigQueryException
from scrapers.utils.logging_config import setup_logging

# Suppress quota project warning for user credentials
warnings.filterwarnings("ignore", message=".*quota project.*")
logger = setup_logging()


def get_gcp_credentials():
    """Load GCP credentials based on configuration method.

    Supports two credential methods:
        - "ADC": Application Default Credentials (gcloud, workload identity, etc.)
        - "FILE": Service account JSON file (set GCP_CREDENTIALS_PATH)

    Returns:
        Credentials object for GCP authentication

    Raises:
        ValueError: If FILE method is selected but path is not set
        FileNotFoundError: If credential file is not found
        Exception: If credential loading fails for any reason
    """
    method = Config.GCP_CREDENTIALS_METHOD
    logger.info(f"Loading GCP credentials using method: {method}")

    if method == "FILE":
        # Load credentials from service account JSON file
        cred_path = Config.GCP_CREDENTIALS_PATH
        if not cred_path:
            raise ValueError(
                'GCP_CREDENTIALS_METHOD is "FILE" but GCP_CREDENTIALS_PATH is not set. '
                "Set GCP_CREDENTIALS_PATH environment variable or in .env"
            )

        if not os.path.exists(cred_path):
            raise FileNotFoundError(f"Credential file not found at: {cred_path}")

        try:
            credentials = google.oauth2.service_account.Credentials.from_service_account_file(cred_path)
            logger.info(f"Successfully loaded credentials from file: {cred_path}")
            return credentials
        except Exception as e:
            logger.error(f"Failed to load credentials from file {cred_path}: {e}")
            raise

    # Default: Application Default Credentials
    try:
        credentials, project = google.auth.default()
        logger.info(f"Successfully loaded Application Default Credentials (project: {project})")
        return credentials
    except Exception as e:
        logger.error(f"Failed to load Application Default Credentials: {e}")
        raise


def get_client() -> bigquery.Client:
    """
    Create and return BigQuery client with discovered credentials.

    Returns:
        Configured BigQuery client with appropriate credentials

    Raises:
        ValueError: If credentials cannot be loaded
        FileNotFoundError: If credential file is missing
    """
    credentials = get_gcp_credentials()
    return bigquery.Client(project=Config.GCP_PROJECT_ID, credentials=credentials)


def load_schema() -> list[bigquery.SchemaField]:
    """
    Load BigQuery table schema from schema.json file.

    Returns:
        List of BigQuery SchemaField objects

    Raises:
        FileNotFoundError: If schema file is not found
    """
    if not Config.SCHEMA_FILE.exists():
        raise FileNotFoundError(f"Schema file not found at {Config.PROJECT_ROOT}/{Config.SCHEMA_FILE}")

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
        raise BigQueryException(f"Unexpected error creating dataset {dataset_id}") from e


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
            logger.info(f"Added new columns to table {table_id}: {[f.name for f in fields_to_add]}")
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
                raise BigQueryException(f"Failed to create table {table_id}") from create_error
        else:
            logger.error(f"Error creating or updating table {table_id}: {e}")
            raise BigQueryException(f"Failed to create or update table {table_id}") from e
    except Exception as e:
        logger.error(f"Unexpected error with table {table_id}: {e}")
        raise BigQueryException(f"Unexpected error with table {table_id}") from e


def load_data_to_staging(client: bigquery.Client, data: list[dict[str, Any]]):
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

    table_ref = client.get_table(table_id)

    job_config = bigquery.LoadJobConfig(
        schema=load_schema(),
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    )

    try:
        logger.info(f"Loading {len(data)} movies to staging table")
        load_job = client.load_table_from_json(data, table_ref, job_config=job_config)
        load_job.result()
        logger.success("Data loaded to staging table successfully")
        return len(data)
    except GoogleCloudError as e:
        logger.error(f"BigQuery error loading to staging: {e}")
        raise BigQueryException(f"Failed to load data to staging: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error loading to staging: {e}")
        raise BigQueryException(f"Unexpected load failure: {e}") from e


def merge_staging_to_main(client: bigquery.Client) -> int:
    """
    Merge data from staging table to main table. Following the schema defined in the SCHEMA_FILE in Config object.

    Args:
        client: BigQuery client instance

    Returns:
        Number of rows affected

    Raises:
        BigQueryException: If merge fails
    """
    target_table = Config.get_full_table_id(Config.TABLE_ID)
    source_table = Config.get_full_table_id(Config.STAGING_TABLE_ID)
    schema = load_schema()

    columns = [col_obj.name for col_obj in schema]
    columns_str = ",".join(columns)
    values_list = [f"source.{col}" if col != "date_updated" else "CURRENT_TIMESTAMP()" for col in columns]
    values_str = ",".join(values_list)
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
        {columns_str}
    )
    VALUES (
        {values_str}
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


def load_movies_to_bigquery(movies: list[dict[str, Any]]) -> int:
    """
    Complete pipeline to load movies to BigQuery.

    Args:
        movies: List of movie dictionaries

    Returns:
        Number of rows merged into main table
    """
    logger.info("Getting client...")
    client = get_client()

    # Setup tables
    logger.info("Setting up BQ Tables...")
    setup_tables(client)

    # Load to staging
    logger.info("Loading data to staging table...")
    rows_loaded = load_data_to_staging(client, movies)
    logger.success(f"Number of rows loaded to staging: {rows_loaded}")

    # Merge to main
    logger.info("Merging staging table to main table...")
    rows_affected = merge_staging_to_main(client)
    logger.debug(f"{rows_affected} rows affected after merging")

    # Clean up staging
    logger.info("Truncating staging table...")
    truncate_staging_table(client)

    return rows_affected
