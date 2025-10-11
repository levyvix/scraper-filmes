from google.cloud import bigquery
import json
from loguru import logger
import warnings

# Suppress the quota project warning for user credentials
warnings.filterwarnings("ignore", message=".*quota project.*")

project_id = "galvanic-flame-384620"


def get_table_schema():
    import os
    from pathlib import Path

    # Get the directory where this script is located
    script_dir = Path(__file__).parent

    # Try multiple paths for schema.json
    schema_paths = [
        script_dir / "schema.json",  # Same directory as this script
        Path("./schema.json"),  # Current working directory
        Path("./gratis_torrent/schema.json"),  # Legacy path
        Path("./src/scrapers/gratis_torrent/schema.json"),  # New structure
    ]

    for path in schema_paths:
        if path.exists():
            with open(path, "r") as f:
                schema = json.load(f)
            logger.info(f"Schema loaded from {path}")
            return schema

    raise FileNotFoundError(f"Schema file not found. Tried: {[str(p) for p in schema_paths]}")


def create_dataset(client: bigquery.Client) -> None:
    dataset_id = "movies_raw"

    dataset = bigquery.Dataset(f"{project_id}.{dataset_id}")
    dataset.location = "US"

    dataset = client.create_dataset(dataset, exists_ok=True)


def create_table(client: bigquery.Client) -> None:
    table_id = f"{project_id}.movies_raw.filmes"
    schema = get_table_schema()

    table = bigquery.Table(table_id, schema=schema)
    table = client.create_table(table, exists_ok=True)


def create_staging_table(client: bigquery.Client) -> None:
    table_id = f"{project_id}.movies_raw.stg_filmes"
    schema = get_table_schema()

    table = bigquery.Table(table_id, schema=schema)
    table = client.create_table(table, exists_ok=True)


def create_load_job(client: bigquery.Client) -> None:
    from pathlib import Path

    table_id_staging = f"{project_id}.movies_raw.stg_filmes"
    table_ref_staging = client.get_table(table_id_staging)

    job_config = bigquery.LoadJobConfig(
        schema=get_table_schema(),
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    )

    # Get the directory where this script is located
    script_dir = Path(__file__).parent

    # Try multiple paths for the JSON file
    json_paths = [
        script_dir / "movies_gratis.json",  # Same directory as this script
        Path("movies_gratis.json"),  # Current working directory
        Path("./gratis_torrent/movies_gratis.json"),  # Legacy path
        Path("./src/scrapers/gratis_torrent/movies_gratis.json"),  # New structure
    ]

    json_path = None
    for path in json_paths:
        if path.exists():
            json_path = path
            break

    if not json_path:
        raise FileNotFoundError(f"JSON file not found. Tried: {[str(p) for p in json_paths]}")

    logger.info(f"Loading data from {json_path}")
    with open(json_path, "r", encoding="utf-8") as f:
        json_file = json.load(f)
        logger.info(f"Loaded {len(json_file)} movies")
        load_job = client.load_table_from_json(
            json_file, table_ref_staging, job_config=job_config
        )

    load_job.result()
    logger.info("Load job completed successfully")


def merge_into(client: bigquery.Client) -> None:
    merge_statement = """
    MERGE INTO `galvanic-flame-384620.movies_raw.filmes` AS target
    USING `galvanic-flame-384620.movies_raw.stg_filmes` AS source
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

    merge_query_res = client.query(merge_statement, location="US")
    merge_query_res.result()
    logger.info(
        f"Merge statement executed successfully: {merge_query_res.num_dml_affected_rows} rows affected"
    )

    # truncate the staging table
    truncate_query = """
    TRUNCATE TABLE `galvanic-flame-384620.movies_raw.stg_filmes`;
    """
    truncate_query_res = client.query(truncate_query, location="US")
    truncate_query_res.result()
    logger.info("Staging table truncated successfully")


def main():
    # Create client with quota project to avoid warnings
    client = bigquery.Client(project=project_id)
    logger.info("Creating dataset and tables")
    create_dataset(client)
    create_staging_table(client)
    create_table(client)
    logger.info("Loading data to staging table")
    create_load_job(client)
    logger.info("Merging data into final table")
    merge_into(client)


if __name__ == "__main__":
    main()
