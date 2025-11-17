# Scraper de Filmes

Sistema automatizado de scraping de filmes do site GratisTorrent/ComandoTorrents e exportação para BigQuery e orquestração com Prefect.

## 🚀 Início Rápido

### Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env com suas configurações (especialmente GCP_PROJECT_ID para BigQuery)
# O arquivo .env é carregado automaticamente pelos scripts
```
### Configurar BigQuery

[BIG_QUERY_SETUP](./docs/BIGQUERY_SETUP.md)

### Executar os Scrapers

```bash
# Scraper do Comando Torrents (simples, sem BigQuery)
uv run run_comando.py

# Scraper do GratisTorrent (com BigQuery e Prefect)
uv run run_gratis.py
```

## 📊 Funcionalidades

### GratisTorrent Scraper
- ✅ Scraping automático do site GratisTorrent
- ✅ Validação de dados com Pydantic
- ✅ Workflow orquestrado com Prefect
- ✅ Exportação opcional para Google BigQuery, com atualização dinâmica de esquema para novas colunas sem perda de dados.
- ✅ Suporte a retry e tratamento de erros

### Comando Torrents Scraper
- ✅ Scraping stealth com bypass de Cloudflare
- ✅ Cache em disco para otimização (DiskCache)
- ✅ Validação de dados com Pydantic
- ✅ Exportação para JSON local
- ✅ Parser robusto com tratamento de erros


## 📂 Estrutura dos Scrapers

### 1. GratisTorrent (`run_gratis.py`)
Scraper completo com integração BigQuery e Prefect. Ideal para produção.

**Localização do módulo:** `scrapers/gratis_torrent/`

**Características:**
- Cliente HTTP customizado com retry
- Integração com BigQuery
- Orquestração Prefect
- Armazenamento SQLite local

### 2. Comando Torrents (`run_comando.py`)
Scraper standalone simplificado focado em performance e stealth.

**Localização do Módulo:** `scrapers/comando_torrents/`

**Características:**
- **Stealth Scraping:** Usa `StealthySession` com bypass de Cloudflare
- **Cache Inteligente:** DiskCache para evitar requisições duplicadas
- **Output JSON:** Salva resultados em `movies.json` localmente
- **Parser Robusto:** Extração de dados com fallbacks e validação

**Modelo de Dados:**
```python
class Movie(BaseModel):
    titulo_dublado: str | None
    titulo_original: str | None
    imdb: str | None
    ano: int | None
    genero: str | None
    tamanho: str | None
    duracao: str | None
    qualidade_video: float | None  # 0-10
    qualidade: str | None
    dublado: bool | None
    sinopse: str | None
    link: str | None
    poster_url: str | None
    date_updated: str | None
```

## 📚 Documentação

- [BIGQUERY_SETUP.md](docs/BIGQUERY_SETUP.md) - Guia de configuração do BigQuery
- [PREFECT_DEPLOYMENT.md](docs/PREFECT_DEPLOYMENT.md) - Guia completo de deployment com Prefect

## 🛠️ Tecnologias

### Core
- **Python 3.11+**
- **UV** - Gerenciamento de dependências
- **Pydantic** - Validação de dados

### GratisTorrent Scraper
- **BeautifulSoup4** - Parsing de HTML
- **SQLAlchemy** - ORM para SQLite
- **Prefect** - Orquestração de workflows
- **Google Cloud BigQuery** - Data warehouse (opcional)
- **Docker** - Containerização

### Comando Torrents Scraper
- **Scrapling** - Stealth scraping com bypass Cloudflare
- **DiskCache** - Cache em disco persistente
- **Pydantic** - Validação de dados

## 📝 Licença

Este projeto é para fins educacionais.
