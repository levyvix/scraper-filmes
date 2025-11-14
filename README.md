# Scraper de Filmes - GratisTorrent

Sistema automatizado de scraping de filmes do site GratisTorrent e Comando Torrents com exportação para BigQuery.

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

### 3. Executar os Scrapers

```bash
# Scraper do GratisTorrent (com BigQuery e Prefect)
uv run main.py

# Scraper do Comando Torrents (simples, sem BigQuery)
uv run src/scrapers/comando_torrents/main.py
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

**Localização:** `src/scrapers/gratis_torrent/`

### 1. GratisTorrent (`flow.py`)
Scraper completo com integração BigQuery e Prefect. Ideal para produção.

**Características:**
- Cliente HTTP customizado com retry
- Integração com BigQuery
- Orquestração Prefect

### 2. Comando Torrents (`src/scrapers/comando_torrents/`)
Scraper standalone simplificado focado em performance e stealth.

**Localização:** `src/scrapers/comando_torrents/main.py`

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
    date_updated: str
    poster_url: str
```

**Uso:**
```bash
# Executar scraper
uv run src/scrapers/comando_torrents/main.py

# Cache é armazenado em ./comando_cache/
# Resultados são salvos em src/scrapers/comando_torrents/movies.json
```

## 📚 Documentação

- [BIGQUERY_SETUP.md](docs/BIGQUERY_SETUP.md) - Guia de configuração do BigQuery
- [PREFECT_DEPLOYMENT.md](docs/PREFECT_DEPLOYMENT.md) - Guia completo de deployment com Prefect (Local)

## 🛠️ Tecnologias

### Core
- **Python 3.11+**
- **UV** - Gerenciamento de dependências
- **Pydantic** - Validação de dados

### GratisTorrent Scraper
- **BeautifulSoup4** - Parsing de HTML
- **Prefect** - Orquestração de workflows
- **Google Cloud BigQuery** - Data warehouse (opcional)

### Comando Torrents Scraper
- **Scrapling** - Stealth scraping com bypass Cloudflare
- **DiskCache** - Cache em disco persistente

## 📝 Licença

Este projeto é para fins educacionais. Nenhuma informação coletada com esse projeto é usado para fins comerciais.
