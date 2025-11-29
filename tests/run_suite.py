"""
Test Suite - Scraper de Filmes
Executa testes de todos os componentes do projeto

Uso:
    uv run python tests/test_suite.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestRunner:
    """Gerenciador de execução de testes"""

    def test(self, name: str, func):
        """Executa um teste e registra resultado"""
        try:
            print(f"\n{'=' * 60}")
            print(f"TEST: {name}")
            print("=" * 60)
            func()
            print("✅ PASSOU")
            self.passed += 1
        except AssertionError as e:
            print(f"❌ FALHOU: {e}")
            self.failed += 1
            self.errors.append((name, str(e)))
        except Exception as e:
            print(f"❌ ERRO: {e}")
            self.failed += 1
            self.errors.append((name, str(e)))

    def summary(self):
        """Imprime resumo dos testes"""
        print(f"\n{'=' * 60}")
        print("RESUMO DOS TESTES")
        print("=" * 60)
        print(f"✅ Passou: {self.passed}")
        print(f"❌ Falhou: {self.failed}")
        print(f"📊 Total: {self.passed + self.failed}")

        if self.errors:
            print(f"\n{'=' * 60}")
            print("ERROS DETALHADOS")
            print("=" * 60)
            for name, error in self.errors:
                print(f"\n{name}:")
                print(f"  {error}")

        return self.failed == 0


# =============================================================================
# TESTES
# =============================================================================


def test_imports():
    """Testa importações dos módulos principais"""
    print("Testando importações...")

    from src.scrapers.gratis_torrent.models import Movie  # noqa: F401

    print("  ✓ src.scrapers.gratis_torrent.models")

    from src.scrapers.gratis_torrent.parser import parse_movie_page  # noqa: F401

    print("  ✓ src.scrapers.gratis_torrent.parser")

    from src.scrapers.gratis_torrent.http_client import fetch_page  # noqa: F401

    print("  ✓ src.scrapers.gratis_torrent.http_client")

    from src.scrapers.gratis_torrent.scraper import scrape_all_movies  # noqa: F401

    print("  ✓ src.scrapers.gratis_torrent.scraper")

    from src.scrapers.gratis_torrent.bigquery_client import (  # noqa: F401
        load_movies_to_bigquery,
    )

    print("  ✓ src.scrapers.gratis_torrent.bigquery_client")

    from src.scrapers.gratis_torrent.flow import gratis_torrent_flow  # noqa: F401

    print("  ✓ src.scrapers.gratis_torrent.flow")

    from src.scrapers.gratis_torrent.config import Config  # noqa: F401

    print("  ✓ src.scrapers.gratis_torrent.config")


def test_pydantic_validation():
    """Testa validação do modelo Pydantic"""
    print("Testando validação Pydantic...")

    from src.scrapers.gratis_torrent.models import Movie
    from pydantic import ValidationError

    # Teste 1: Dados válidos
    movie = Movie(
        titulo_dublado="Vingadores",
        titulo_original="The Avengers",
        imdb=8.0,
        ano=2012,
        genero="Ação, Aventura",
        tamanho="2.5",
        duracao_minutos=143,
        qualidade_video=9.0,
        qualidade="1080p BluRay",
        dublado=True,
        sinopse="Super-heróis se unem",
        link="http://example.com",
    )
    print(f"  ✓ Dados válidos aceitos: {movie.titulo_dublado}")
    assert movie.qualidade_video == 9.0, "qualidade_video deve ser float"
    assert movie.qualidade == "1080p BluRay", "qualidade deve ser string"

    # Teste 2: IMDB inválido
    try:
        Movie(
            titulo_dublado="Teste",
            titulo_original="Test",
            imdb=15.0,
            ano=2020,
            genero="Drama",
            tamanho="1.0",
            duracao_minutos=90,
            qualidade_video=8.0,
            qualidade="720p",
            dublado=True,
            sinopse="Teste",
            link="http://example.com",
        )
        raise AssertionError("IMDB > 10 deveria ser rejeitado")
    except ValidationError:
        print("  ✓ IMDB inválido rejeitado")

    # Teste 3: Ano inválido
    try:
        Movie(
            titulo_dublado="Teste",
            titulo_original="Test",
            imdb=7.0,
            ano=1800,
            genero="Drama",
            tamanho="1.0",
            duracao_minutos=90,
            qualidade_video=8.0,
            qualidade="720p",
            dublado=True,
            sinopse="Teste",
            link="http://example.com",
        )
        raise AssertionError("Ano < 1888 deveria ser rejeitado")
    except ValidationError:
        print("  ✓ Ano inválido rejeitado")


def test_config():
    """Testa configurações do projeto"""
    print("Testando configurações...")

    from src.scrapers.gratis_torrent.config import Config

    # Verificar propriedades essenciais
    assert Config.GCP_PROJECT_ID is not None, "GCP_PROJECT_ID não configurado"
    print(f"  ✓ GCP_PROJECT_ID: {Config.GCP_PROJECT_ID}")

    assert Config.DATASET_ID == "movies_raw", "DATASET_ID incorreto"
    print(f"  ✓ DATASET_ID: {Config.DATASET_ID}")

    assert Config.TABLE_ID == "filmes", "TABLE_ID incorreto"
    print(f"  ✓ TABLE_ID: {Config.TABLE_ID}")

    assert Config.LOCATION == "US", "LOCATION incorreto"
    print(f"  ✓ LOCATION: {Config.LOCATION}")

    # Verificar métodos
    full_table_id = Config.get_full_table_id(Config.TABLE_ID)
    assert "movies_raw.filmes" in full_table_id, "get_full_table_id incorreto"
    print(f"  ✓ Full table ID: {full_table_id}")


def test_parser_functions():
    """Testa funções do parser"""
    print("Testando funções do parser...")

    from src.scrapers.gratis_torrent.parser import (
        clean_genre,
        safe_convert_float,
        safe_convert_int,
        extract_regex_field,
    )

    # Teste 1: clean_genre
    assert clean_genre("Action / Sci-Fi") == "Action, Sci-Fi"
    print("  ✓ clean_genre funciona")

    # Teste 2: safe_convert_float
    assert safe_convert_float("8.5") == 8.5
    assert safe_convert_float("invalid") is None
    print("  ✓ safe_convert_float funciona")

    # Teste 3: safe_convert_int
    assert safe_convert_int("120") == 120
    assert safe_convert_int("invalid") is None
    print("  ✓ safe_convert_int funciona")

    # Teste 4: extract_regex_field
    text = "Título: The Matrix"
    pattern = r"Título:\s*(.+)"
    assert extract_regex_field(pattern, text) == "The Matrix"
    print("  ✓ extract_regex_field funciona")


def test_model_serialization():
    """Testa serialização do modelo"""
    print("Testando serialização do modelo...")

    from src.scrapers.gratis_torrent.models import Movie

    movie = Movie(
        titulo_dublado="Matrix",
        titulo_original="The Matrix",
        imdb=8.7,
        ano=1999,
        genero="Action, Sci-Fi",
        tamanho="2.5",
        duracao_minutos=136,
        qualidade_video=10.0,
        qualidade="1080p BluRay",
        dublado=True,
        sinopse="A hacker discovers reality.",
        link="https://example.com/matrix",
    )

    # Teste model_dump
    data = movie.model_dump()
    assert isinstance(data, dict), "model_dump deve retornar dict"
    assert data["titulo_dublado"] == "Matrix", "Título incorreto"
    assert data["imdb"] == 8.7, "IMDB incorreto"
    print("  ✓ model_dump funciona")

    # Verificar todos os campos
    required_fields = [
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
    ]

    for field in required_fields:
        assert field in data, f"Campo '{field}' não encontrado"

    print(f"  ✓ Todos os {len(required_fields)} campos presentes")


def test_prefect_flow_structure():
    """Testa estrutura do Prefect Flow"""
    print("Testando estrutura do Prefect Flow...")

    from src.scrapers.gratis_torrent.flow import (
        gratis_torrent_flow,
        scrape_movies_task,
        load_to_bigquery_task,
    )

    # Verificar se é um flow
    print(f"  ✓ Flow: {gratis_torrent_flow.name}")

    # Verificar tasks
    tasks = [
        (scrape_movies_task, "scrape-movies"),
        (load_to_bigquery_task, "load-to-bigquery"),
    ]

    for task, expected_name in tasks:
        assert task.name == expected_name, f"Nome da task incorreto: {task.name}"
        print(f"  ✓ Task: {task.name}")

    # Verificar retries configurados
    assert scrape_movies_task.retries == 2, "scrape_movies_task deve ter 2 retries"
    assert load_to_bigquery_task.retries == 3, "load_to_bigquery_task deve ter 3 retries"
    print("  ✓ Retries configurados corretamente")


def test_http_client_functions():
    """Testa funções do http_client"""
    print("Testando funções do http_client...")

    from src.scrapers.gratis_torrent.http_client import collect_movie_links
    from bs4 import BeautifulSoup

    # Teste collect_movie_links com HTML mockado
    html = """
    <html>
        <div id="capas_pequenas">
            <div><a href="https://example.com/movie1">Movie 1</a></div>
            <div><a href="https://example.com/movie2">Movie 2</a></div>
            <div><a href="https://example.com/movie1">Movie 1 Again</a></div>
        </div>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    links = collect_movie_links(soup)

    assert len(links) == 2, "Deduplicação de links falhou"
    assert "https://example.com/movie1" in links
    assert "https://example.com/movie2" in links
    print(f"  ✓ collect_movie_links funciona (encontrou {len(links)} links únicos)")


def test_bigquery_schema():
    """Testa schema do BigQuery"""
    print("Testando schema do BigQuery...")

    import json
    from src.scrapers.gratis_torrent.config import Config

    # Carregar schema
    schema_file = Config.SCHEMA_FILE
    assert schema_file.exists(), f"Schema file não encontrado: {schema_file}"

    with open(schema_file, "r") as f:
        schema = json.load(f)

    # Verificar estrutura do schema
    assert isinstance(schema, list), "Schema deve ser uma lista"
    print(f"  ✓ Schema carregado com {len(schema)} campos")

    # Verificar campos essenciais
    field_names = [field["name"] for field in schema]
    required_fields = [
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
    ]

    for field in required_fields:
        assert field in field_names, f"Campo '{field}' não encontrado no schema"

    print(f"  ✓ Todos os {len(required_fields)} campos essenciais presentes")

    # Verificar tipos de dados
    type_mapping = {
        "titulo_dublado": "STRING",
        "imdb": "FLOAT64",
        "ano": "INT64",
        "dublado": "BOOL",
        "date_updated": "TIMESTAMP",
    }

    for field_name, expected_type in type_mapping.items():
        field = next(f for f in schema if f["name"] == field_name)
        assert field["type"] == expected_type, f"Tipo incorreto para {field_name}"

    print("  ✓ Tipos de dados corretos no schema")


# =============================================================================
# MAIN
# =============================================================================


def main():
    """Executa todos os testes"""
    print("\n" + "=" * 60)
    print("🧪 SUITE DE TESTES - SCRAPER DE FILMES")
    print("=" * 60)

    runner = TestRunner()

    # Executar testes
    runner.test("1. Importações dos Módulos", test_imports)
    runner.test("2. Validação Pydantic", test_pydantic_validation)
    runner.test("3. Configurações", test_config)
    runner.test("4. Funções do Parser", test_parser_functions)
    runner.test("5. Serialização do Modelo", test_model_serialization)
    runner.test("6. Estrutura do Prefect Flow", test_prefect_flow_structure)
    runner.test("7. Funções do HTTP Client", test_http_client_functions)
    runner.test("8. Schema do BigQuery", test_bigquery_schema)

    # Resumo
    success = runner.summary()

    print("\n" + "=" * 60)
    if success:
        print("🎉 TODOS OS TESTES PASSARAM!")
    else:
        print("⚠️  ALGUNS TESTES FALHARAM")
    print("=" * 60 + "\n")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
