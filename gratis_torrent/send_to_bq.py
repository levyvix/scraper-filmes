from google.cloud import bigquery
import json
from loguru import logger

project_id = "galvanic-flame-384620"


def get_table_schema():
    with open("schema.json", "r") as f:
        schema = json.load(f)

    return schema


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
    table_id_staging = f"{project_id}.movies_raw.stg_filmes"
    table_ref_staging = client.get_table(table_id_staging)

    job_config = bigquery.LoadJobConfig(
        schema=get_table_schema(),
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    )

    with open("movies_gratis.json", "r", encoding="utf-8") as f:
        json_file = json.load(f)
        logger.debug(json_file)
        load_job = client.load_table_from_json(
            json_file, table_ref_staging, job_config=job_config
        )

    load_job.result()


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
    client = bigquery.Client()
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
