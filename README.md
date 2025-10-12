# Scraper de Filmes - GratisTorrent

Sistema automatizado de scraping de filmes do site GratisTorrent e exportação para BigQuery.

## 🚀 Início Rápido

### 1. Instalar Dependências

```bash
# O projeto usa UV para gerenciamento de dependências
uv sync
```

### 2. Configurar Variáveis de Ambiente (Opcional)

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env com suas configurações (especialmente GCP_PROJECT_ID para BigQuery)
# O arquivo .env é carregado automaticamente pelos scripts
```

### 3. Executar o Scraper

```bash
# Scraper do GratisTorrent
uv run main.py
```

## 📊 Funcionalidades

- ✅ Scraping automático do site GratisTorrent
- ✅ Validação de dados com Pydantic
- ✅ Workflow orquestrado com Prefect
- ✅ Exportação opcional para Google BigQuery
- ✅ Suporte a retry e tratamento de erros


## 📚 Documentação

- [BIGQUERY_SETUP.md](docs/BIGQUERY_SETUP.md) - Guia de configuração do BigQuery
- [PREFECT_DEPLOYMENT.md](docs/PREFECT_DEPLOYMENT.md) - Guia completo de deployment com Prefect

## 🛠️ Tecnologias

- **Python 3.11+**
- **UV** - Gerenciamento de dependências
- **BeautifulSoup4** - Parsing de HTML
- **Pydantic** - Validação de dados
- **SQLAlchemy** - ORM para SQLite
- **Prefect** - Orquestração de workflows
- **Google Cloud BigQuery** - Data warehouse (opcional)
- **Docker** - Containerização

## 📝 Licença

Este projeto é para fins educacionais.
