#!/usr/bin/env python3
"""
Script para testar a inserção de dados no BigQuery.

Requisitos:
1. Ter o Google Cloud SDK instalado e autenticado
2. Ter permissões no projeto BigQuery
3. Configurar a variável GOOGLE_APPLICATION_CREDENTIALS (opcional)

Uso:
    uv run python test_bigquery.py
"""
import os
import sys
from pathlib import Path
import warnings

# Suppress the quota project warning for user credentials
warnings.filterwarnings("ignore", message=".*quota project.*")

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from google.cloud import bigquery
from loguru import logger

# Change to project root directory
os.chdir(project_root)


def check_credentials():
    """Verifica se as credenciais estão configuradas"""
    logger.info("Verificando credenciais do Google Cloud...")

    # Método 1: Variável de ambiente GOOGLE_APPLICATION_CREDENTIALS
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if creds_path:
        if os.path.exists(creds_path):
            logger.success(f"✓ Credenciais encontradas em: {creds_path}")
            return True
        else:
            logger.warning(f"⚠ Arquivo de credenciais não existe: {creds_path}")

    # Método 2: Application Default Credentials (gcloud auth application-default login)
    try:
        from google.auth import default
        credentials, project = default()
        if credentials:
            logger.success(f"✓ Application Default Credentials configuradas")
            logger.info(f"  Projeto: {project if project else 'não definido'}")
            return True
    except Exception as e:
        logger.warning(f"⚠ Falha ao carregar Application Default Credentials: {e}")

    logger.error("✗ Nenhuma credencial válida encontrada!")
    return False


def test_connection():
    """Testa conexão com o BigQuery"""
    logger.info("Testando conexão com BigQuery...")

    try:
        # Specify project to avoid quota warnings
        client = bigquery.Client(project="galvanic-flame-384620")
        logger.info(f"Cliente BigQuery criado para projeto: {client.project}")

        # Listar datasets como teste
        datasets = list(client.list_datasets())
        if datasets:
            logger.success(f"✓ Conexão bem-sucedida! Datasets encontrados:")
            for dataset in datasets[:5]:  # Mostrar apenas os 5 primeiros
                logger.info(f"  - {dataset.dataset_id}")
        else:
            logger.info("  Nenhum dataset encontrado no projeto")

        return True

    except Exception as e:
        logger.error(f"✗ Erro ao conectar: {e}")
        return False


def run_bigquery_import():
    """Executa a importação para o BigQuery"""
    logger.info("Iniciando importação para BigQuery...")

    try:
        from src.scrapers.gratis_torrent.send_to_bq import main
        main()
        logger.success("✓ Importação concluída com sucesso!")
        return True
    except Exception as e:
        logger.error(f"✗ Erro durante importação: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def main():
    logger.info("=" * 60)
    logger.info("TESTE DE INSERÇÃO NO BIGQUERY")
    logger.info("=" * 60)

    # Passo 1: Verificar credenciais
    if not check_credentials():
        logger.error("\nConfigure as credenciais usando um dos métodos:")
        logger.info("1. Variável de ambiente:")
        logger.info("   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json")
        logger.info("\n2. Application Default Credentials:")
        logger.info("   gcloud auth application-default login")
        return 1

    logger.info("")

    # Passo 2: Testar conexão
    if not test_connection():
        logger.error("\nFalha na conexão. Verifique:")
        logger.info("1. Se você tem acesso ao projeto 'galvanic-flame-384620'")
        logger.info("2. Se as permissões do BigQuery estão configuradas")
        return 1

    logger.info("")

    # Passo 3: Executar importação
    if run_bigquery_import():
        logger.success("\n✓ TESTE CONCLUÍDO COM SUCESSO!")
        return 0
    else:
        logger.error("\n✗ TESTE FALHOU")
        return 1


if __name__ == "__main__":
    sys.exit(main())
