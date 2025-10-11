# Scraper de Filmes - GratisTorrent

Sistema automatizado de scraping de filmes do site GratisTorrent com armazenamento em SQLite e exportação opcional para BigQuery.

## 📁 Estrutura do Projeto

```
scraper-filmes/
├── src/
│   ├── scrapers/
│   │   └── gratis_torrent/     # Scraper do GratisTorrent
│   │       ├── extract.py       # Script de scraping
│   │       ├── send_to_bq.py    # Exportação para BigQuery
│   │       └── schema.json      # Schema do BigQuery
│   ├── database/
│   │   └── insert_to_database.py  # Lógica de inserção no SQLite
│   └── flows/
│       └── prefect_flow_gratis.py # Flow do Prefect
├── scripts/
│   └── test_bigquery.py         # Script de teste do BigQuery
├── config/
│   └── prefect.yaml             # Configuração do Prefect
├── deploy/
│   ├── Dockerfile               # Docker para deployment
│   ├── docker-compose.yaml      # Docker Compose
│   └── docker_deploy.py         # Script de deployment
├── docs/
│   ├── CLAUDE.md                # Documentação do projeto
│   └── BIGQUERY_SETUP.md        # Guia de configuração do BigQuery
├── dbs/
│   └── movie_database.db        # Banco de dados SQLite
└── pyproject.toml               # Dependências do projeto
```

## 🚀 Início Rápido

### 1. Instalar Dependências

```bash
# O projeto usa UV para gerenciamento de dependências
uv sync
```

### 2. Executar o Scraper

```bash
# Scraper do GratisTorrent
uv run src/scrapers/gratis_torrent/extract.py
```

### 3. Executar o Flow Completo

```bash
# Flow do Prefect (scraping + banco de dados + estatísticas)
uv run src/flows/prefect_flow_gratis.py
```

## 📊 Funcionalidades

- ✅ Scraping automático do site GratisTorrent
- ✅ Validação de dados com Pydantic
- ✅ Armazenamento em SQLite com deduplicação
- ✅ Workflow orquestrado com Prefect
- ✅ Exportação opcional para Google BigQuery
- ✅ Deployment com Docker
- ✅ Suporte a retry e tratamento de erros

## 🔧 Comandos Mais Importantes

### 🎯 Uso Rápido (Recomendado)

```bash
# Executar o workflow completo (scraping + banco de dados + estatísticas)
uv run src/flows/prefect_flow_gratis.py
```

### ⚙️ Gerenciamento de Dependências

```bash
# Instalar/sincronizar dependências
uv sync

# Adicionar nova biblioteca
uv add nome-da-biblioteca

# Remover biblioteca
uv remove nome-da-biblioteca

# Executar qualquer script Python
uv run src/caminho/para/script.py
```

### 🕷️ Scraping Manual

```bash
# Executar scraper do GratisTorrent
uv run src/scrapers/gratis_torrent/extract.py

# Inserir dados manualmente no SQLite
uv run python -c "from src.database.insert_to_database import create_and_insert; from sqlalchemy import create_engine; create_and_insert('src/scrapers/gratis_torrent/movies_gratis.json', create_engine('sqlite:///dbs/movie_database.db'))"
```

### 🔄 Prefect (Orquestração)

```bash
# Executar flow localmente
uv run src/flows/prefect_flow_gratis.py

# Iniciar servidor Prefect (interface web)
prefect server start

# Criar deployment para agendamento
prefect deployment build src/flows/prefect_flow_gratis.py:gratis_torrent_flow \
  --name gratis_flow \
  -q padrao \
  --apply

# Iniciar agent para executar deployments
prefect agent start -q padrao

# Ver status dos flows
prefect flow-run ls
```

### 📊 BigQuery (Opcional)

```bash
# Autenticar com Google Cloud
gcloud auth application-default login

# Testar conexão com BigQuery
uv run scripts/test_bigquery.py

# Enviar dados para BigQuery
uv run src/scrapers/gratis_torrent/send_to_bq.py

# Para configuração completa, veja docs/BIGQUERY_SETUP.md
```

### 🗄️ Banco de Dados

```bash
# Ver tabelas do banco
sqlite3 dbs/movie_database.db ".tables"

# Ver filmes cadastrados
sqlite3 dbs/movie_database.db "SELECT titulo_dublado, ano, imdb FROM movies LIMIT 10;"

# Contar filmes no banco
sqlite3 dbs/movie_database.db "SELECT COUNT(*) FROM movies;"

# Ver estrutura da tabela
sqlite3 dbs/movie_database.db ".schema movies"
```

### 🐳 Docker

```bash
# Build da imagem
docker build -t scraper-filmes -f deploy/Dockerfile .

# Executar com docker-compose
docker-compose -f deploy/docker-compose.yaml up

# Parar containers
docker-compose -f deploy/docker-compose.yaml down

# Ver logs
docker-compose -f deploy/docker-compose.yaml logs -f
```

### 🧹 Utilitários

```bash
# Limpar cache Python
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Ver versão do Python
python --version

# Ver localização do ambiente virtual UV
which python
```

## 📦 Estrutura de Dados

### Campos do Filme

| Campo            | Tipo    | Descrição                    |
|------------------|---------|------------------------------|
| titulo_dublado   | STRING  | Título em português          |
| titulo_original  | STRING  | Título original              |
| imdb             | FLOAT   | Nota do IMDB                 |
| ano              | INTEGER | Ano de lançamento            |
| genero           | STRING  | Gêneros (separados por ",")  |
| tamanho          | STRING  | Tamanho do arquivo (GB)      |
| duracao_minutos  | INTEGER | Duração em minutos           |
| qualidade_video  | FLOAT   | Qualidade do vídeo (0-10)    |
| qualidade        | STRING  | Qualidade (1080p, 720p, etc) |
| dublado          | BOOLEAN | Se está dublado              |
| sinopse          | STRING  | Sinopse do filme             |
| link             | STRING  | URL do torrent               |

## 🐳 Docker

```bash
# Build da imagem
docker build -t scraper-filmes -f deploy/Dockerfile .

# Executar com docker-compose
docker-compose -f deploy/docker-compose.yaml up
```

## 📚 Documentação

- [CLAUDE.md](docs/CLAUDE.md) - Documentação completa do projeto
- [BIGQUERY_SETUP.md](docs/BIGQUERY_SETUP.md) - Guia de configuração do BigQuery

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
