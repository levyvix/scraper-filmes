import json
from scrapers.gratis_torrent.config import Config


def test_bigquery_schema():
    """Tests the BigQuery schema file."""
    schema_file = Config.SCHEMA_FILE
    assert schema_file.exists(), f"Schema file not found: {schema_file}"

    with open(schema_file, "r") as f:
        schema = json.load(f)

    assert isinstance(schema, list)

    field_names = {field["name"] for field in schema}
    required_fields = {
        "titulo_dublado",
        "titulo_original",
        "imdb",
        "ano",
        "genero",
        "tamanho",
        "duracao_minutos",
        "qualidade_video",
        "qualidade",
        "dublado",
        "sinopse",
        "link",
        "date_updated",
    }

    assert required_fields.issubset(field_names)

    type_mapping = {
        "titulo_dublado": "STRING",
        "imdb": "FLOAT64",
        "ano": "INT64",
        "dublado": "BOOL",
        "date_updated": "TIMESTAMP",
    }

    schema_map = {field["name"]: field["type"] for field in schema}
    for field_name, expected_type in type_mapping.items():
        assert schema_map[field_name] == expected_type
