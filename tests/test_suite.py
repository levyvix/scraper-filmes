"""
Teste Suite Completo - Scraper de Filmes
Executa testes de todos os componentes do projeto

Uso:
    uv run python tests/test_suite.py
"""

import sys
import os
import json
import tempfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestRunner:
    """Gerenciador de execução de testes"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def test(self, name: str, func):
        """Executa um teste e registra resultado"""
        try:
            print(f"\n{'='*60}")
            print(f"TEST: {name}")
            print('='*60)
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
        print(f"\n{'='*60}")
        print("RESUMO DOS TESTES")
        print('='*60)
        print(f"✅ Passou: {self.passed}")
        print(f"❌ Falhou: {self.failed}")
        print(f"📊 Total: {self.passed + self.failed}")

        if self.errors:
            print(f"\n{'='*60}")
            print("ERROS DETALHADOS")
            print('='*60)
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

    from src.scrapers.gratis_torrent.extract import Movie  # noqa: F401
    print("  ✓ src.scrapers.gratis_torrent.extract")

    from src.database.insert_to_database import create_and_insert  # noqa: F401
    print("  ✓ src.database.insert_to_database")

    from src.flows.prefect_flow_gratis import gratis_torrent_flow  # noqa: F401
    print("  ✓ src.flows.prefect_flow_gratis")

    import src.scrapers.gratis_torrent.send_to_bq  # noqa: F401
    print("  ✓ src.scrapers.gratis_torrent.send_to_bq")


def test_database_schema():
    """Testa criação do schema do banco de dados"""
    print("Testando schema do banco de dados...")

    from sqlalchemy import create_engine, inspect
    from src.database.insert_to_database import Base

    # Criar banco em memória
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)

    # Inspecionar schema
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    print(f"  ✓ Tabelas criadas: {tables}")
    assert 'movies' in tables, "Tabela 'movies' não encontrada"
    assert 'genres' in tables, "Tabela 'genres' não encontrada"

    # Verificar colunas da tabela movies
    movies_columns = [col['name'] for col in inspector.get_columns('movies')]
    print(f"  ✓ Colunas movies: {len(movies_columns)} campos")

    required_fields = [
        'id', 'titulo_dublado', 'titulo_original', 'imdb', 'ano',
        'tamanho_mb', 'duracao_minutos', 'qualidade_video', 'qualidade',
        'dublado', 'sinopse', 'date_updated', 'link'
    ]

    for field in required_fields:
        assert field in movies_columns, f"Campo '{field}' não encontrado em movies"

    # Verificar colunas da tabela genres
    genres_columns = [col['name'] for col in inspector.get_columns('genres')]
    print(f"  ✓ Colunas genres: {len(genres_columns)} campos")

    assert 'genre' in genres_columns, "Campo 'genre' não encontrado em genres"
    assert 'movie_id' in genres_columns, "Campo 'movie_id' não encontrado em genres"


def test_pydantic_validation():
    """Testa validação do modelo Pydantic"""
    print("Testando validação Pydantic...")

    from src.scrapers.gratis_torrent.extract import Movie
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
        link="http://example.com"
    )
    print(f"  ✓ Dados válidos aceitos: {movie.titulo_dublado}")
    assert movie.qualidade_video == 9.0, "qualidade_video deve ser float"
    assert movie.qualidade == "1080p BluRay", "qualidade deve ser string"

    # Teste 2: IMDB inválido
    try:
        Movie(
            titulo_dublado="Teste", titulo_original="Test", imdb=15.0,
            ano=2020, genero="Drama", tamanho="1.0", duracao_minutos=90,
            qualidade_video=8.0, qualidade="720p", dublado=True,
            sinopse="Teste", link="http://example.com"
        )
        raise AssertionError("IMDB > 10 deveria ser rejeitado")
    except ValidationError:
        print("  ✓ IMDB inválido rejeitado")

    # Teste 3: Ano inválido
    try:
        Movie(
            titulo_dublado="Teste", titulo_original="Test", imdb=7.0,
            ano=1800, genero="Drama", tamanho="1.0", duracao_minutos=90,
            qualidade_video=8.0, qualidade="720p", dublado=True,
            sinopse="Teste", link="http://example.com"
        )
        raise AssertionError("Ano < 1888 deveria ser rejeitado")
    except ValidationError:
        print("  ✓ Ano inválido rejeitado")


def test_database_insertion():
    """Testa inserção de dados no banco"""
    print("Testando inserção no banco de dados...")

    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from src.database.insert_to_database import create_and_insert, Movie, Genre

    # Criar JSON de teste
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        test_data = [
            {
                "titulo_dublado": "Teste Filme 1",
                "titulo_original": "Test Movie 1",
                "imdb": 8.5,
                "ano": 2023,
                "genero": "Ação, Aventura, Drama",
                "tamanho": "2.5",
                "duracao_minutos": 120,
                "qualidade_video": 9.0,
                "qualidade": "1080p BluRay",
                "dublado": True,
                "sinopse": "Um filme de teste",
                "link": "http://example.com/movie1"
            },
            {
                "titulo_dublado": "Teste Filme 2",
                "titulo_original": "Test Movie 2",
                "imdb": 7.2,
                "ano": 2024,
                "genero": "Comédia | Romance",
                "tamanho": "1.8",
                "duracao_minutos": 95,
                "qualidade_video": 8.5,
                "qualidade": "720p WEB-DL",
                "dublado": False,
                "sinopse": "Outro filme de teste",
                "link": "http://example.com/movie2"
            }
        ]
        json.dump(test_data, f)
        json_path = f.name

    try:
        # Criar banco de teste
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        engine = create_engine(f'sqlite:///{db_path}')

        # Inserir dados
        create_and_insert(json_path, engine)
        print("  ✓ Dados inseridos")

        # Verificar inserção
        with Session(engine) as sess:
            movies = sess.query(Movie).all()
            assert len(movies) == 2, f"Esperado 2 filmes, encontrado {len(movies)}"
            print(f"  ✓ {len(movies)} filmes inseridos")

            # Verificar campos
            movie1 = movies[0]
            assert movie1.qualidade_video == 9.0, "qualidade_video incorreto"
            assert movie1.qualidade == "1080p BluRay", "qualidade incorreto"
            assert movie1.tamanho_mb == 2560.0, "conversão GB->MB incorreta"
            print("  ✓ Campos corretos (qualidade_video, qualidade, tamanho_mb)")

            # Verificar gêneros
            genres = sess.query(Genre).filter_by(movie_id=movie1.id).all()
            assert len(genres) == 3, f"Esperado 3 gêneros, encontrado {len(genres)}"
            genre_names = [g.genre for g in genres]
            assert "Ação" in genre_names, "Gênero 'Ação' não encontrado"
            print(f"  ✓ Gêneros separados corretamente: {', '.join(genre_names)}")

    finally:
        # Cleanup
        os.unlink(json_path)
        os.unlink(db_path)


def test_deduplication():
    """Testa deduplicação de filmes"""
    print("Testando deduplicação...")

    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from src.database.insert_to_database import create_and_insert, Movie

    # Criar JSON de teste
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        test_data = [{
            "titulo_dublado": "Teste Dedup",
            "titulo_original": "Test Dedup",
            "imdb": 8.0,
            "ano": 2023,
            "genero": "Drama",
            "tamanho": "2.0",
            "duracao_minutos": 100,
            "qualidade_video": 8.0,
            "qualidade": "1080p",
            "dublado": True,
            "sinopse": "Teste",
            "link": "http://example.com/dedup"
        }]
        json.dump(test_data, f)
        json_path = f.name

    try:
        # Criar banco de teste
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        engine = create_engine(f'sqlite:///{db_path}')

        # Primeira inserção
        create_and_insert(json_path, engine)

        with Session(engine) as sess:
            count1 = sess.query(Movie).count()
            print(f"  ✓ Primeira inserção: {count1} filme")

        # Segunda inserção (deve ignorar duplicatas)
        create_and_insert(json_path, engine)

        with Session(engine) as sess:
            count2 = sess.query(Movie).count()
            print(f"  ✓ Segunda inserção: {count2} filme")

        assert count1 == count2 == 1, "Deduplicação falhou"
        print("  ✓ Deduplicação funcionando")

    finally:
        # Cleanup
        os.unlink(json_path)
        os.unlink(db_path)


def test_env_loading():
    """Testa carregamento de variáveis de ambiente"""
    print("Testando carregamento de .env...")

    import os
    from dotenv import load_dotenv

    # Criar .env temporário
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, dir='.') as f:
        f.write("TEST_VAR=test_value_123\n")
        env_path = f.name

    try:
        # Carregar .env
        load_dotenv(env_path)

        value = os.getenv("TEST_VAR")
        assert value == "test_value_123", f"Esperado 'test_value_123', obtido '{value}'"
        print(f"  ✓ Variável carregada: TEST_VAR={value}")

        # Limpar variável
        if "TEST_VAR" in os.environ:
            del os.environ["TEST_VAR"]

    finally:
        # Cleanup
        os.unlink(env_path)


def test_prefect_flow_structure():
    """Testa estrutura do Prefect Flow"""
    print("Testando estrutura do Prefect Flow...")

    from src.flows.prefect_flow_gratis import (
        gratis_torrent_flow,
        run_gratis_scraper,
        insert_movies,
        get_stats,
        export_to_bigquery
    )
    import inspect

    # Verificar se é um flow
    print(f"  ✓ Flow: {gratis_torrent_flow.name}")

    # Verificar parâmetros
    sig = inspect.signature(gratis_torrent_flow.fn)
    params = list(sig.parameters.keys())
    assert 'export_bq' in params, "Parâmetro 'export_bq' não encontrado"
    print(f"  ✓ Parâmetros: {', '.join(params)}")

    # Verificar tasks
    tasks = [
        (run_gratis_scraper, "Run GratisTorrent Scraper"),
        (insert_movies, "Insert into database"),
        (get_stats, "Get Movie Stats"),
        (export_to_bigquery, "Export to BigQuery")
    ]

    for task, expected_name in tasks:
        assert task.name == expected_name, f"Nome da task incorreto: {task.name}"
        print(f"  ✓ Task: {task.name}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Executa todos os testes"""
    print("\n" + "="*60)
    print("🧪 SUITE DE TESTES - SCRAPER DE FILMES")
    print("="*60)

    runner = TestRunner()

    # Executar testes
    runner.test("1. Importações dos Módulos", test_imports)
    runner.test("2. Schema do Banco de Dados", test_database_schema)
    runner.test("3. Validação Pydantic", test_pydantic_validation)
    runner.test("4. Inserção no Banco", test_database_insertion)
    runner.test("5. Deduplicação", test_deduplication)
    runner.test("6. Carregamento de .env", test_env_loading)
    runner.test("7. Estrutura do Prefect Flow", test_prefect_flow_structure)

    # Resumo
    success = runner.summary()

    print("\n" + "="*60)
    if success:
        print("🎉 TODOS OS TESTES PASSARAM!")
    else:
        print("⚠️  ALGUNS TESTES FALHARAM")
    print("="*60 + "\n")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
