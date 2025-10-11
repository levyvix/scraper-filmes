# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a web scraping project that extracts movie information from gratistorrent.com and stores it in a database. The project uses requests + BeautifulSoup for scraping, SQLAlchemy for database operations, and Prefect for workflow orchestration. Data is stored in SQLite locally and can be exported to Google BigQuery.

## Core Architecture

### Scraping Pipeline

**GratisTorrent Pipeline**
- Scraper: `gratis_torrent/extract.py`
- Uses requests + BeautifulSoup for HTML parsing
- Pydantic `Movie` model for data validation
- Extracts: titulo_dublado, titulo_original, imdb, ano, genero, tamanho, duracao_minutos, qualidade_video, qualidade, dublado, sinopse, link
- Outputs to `movies_gratis.json`
- Can export to BigQuery via `gratis_torrent/send_to_bq.py`

### Database Layer

- **Models**: `insert_to_database.py` defines SQLAlchemy models
  - `Movie` table: stores movie metadata
  - `Gender` table: stores genres (many-to-many relationship with movies)
- **Database**: SQLite at `dbs/movie_database.db`
- Deduplication: Movies checked by `titulo_dublado` + `date_updated` before insertion

### Workflow Orchestration

- **Prefect Flow**: `prefect_flow_se.py` contains the `comandola_filmes` flow
  - Task 1: Run Scrapy spider to generate `filmes.json`
  - Task 2: Insert JSON data into SQLite database
  - Task 3: Send email notification with last 20 movies
- **Email Notifications**: `filmes/send_email/send_email.py` sends daily email summaries using yagmail
- **Docker Deployment**: `docker_deploy.py` creates Prefect deployment with Docker infrastructure

## Development Commands

### Dependency Management
```bash
# Add new dependency
uv add package-name

# Run Python scripts
uv run script.py
```

### Running the Scraper

```bash
# GratisTorrent scraper
uv run gratis_torrent/extract.py
# Outputs to movies_gratis.json
```

### Database Operations

```bash
# Insert scraped data into SQLite
uv run insert_to_database.py

# The script expects movies_gratis.json and creates dbs/movie_database.db
```

### Prefect Workflow

```bash
# Run flow locally
uv run prefect_flow_gratis.py

# Start Prefect server
prefect server start

# Build and apply deployment
prefect deployment build prefect_flow_gratis.py:gratis_torrent_flow --name gratis_flow -q padrao --apply

# Start agent
prefect agent start -q padrao

# Run deployment
prefect deployment run "GratisTorrent Flow/gratis_flow"
```

### Docker Deployment

```bash
# Build and push Docker image
docker image build -t levyvix/gratis_torrent:tag .
docker image push levyvix/gratis_torrent:tag

# Configure Docker Container block in Prefect UI, then:
uv run docker_deploy.py

# Start agent
prefect agent start -q dev

# Run flow
prefect run "GratisTorrent Flow/gratis_torrent_flow"

# Or use docker-compose
docker-compose up
```

### Code Quality

```bash
# Linting configured via ruff.toml
ruff check .
```

## Important Implementation Details

### GratisTorrent Scraper Logic (`gratis_torrent/extract.py`)

- Uses requests + BeautifulSoup for simple, reliable scraping
- Extracts movie card links from homepage using CSS selectors
- `extract_info()` parses individual movie pages with regex patterns
- Handles Portuguese text and Brazilian date formats
- Pydantic model validation ensures data quality before saving

### Database Schema

- Movies use auto-incrementing integer primary keys
- Genres stored in separate table with foreign key to movies
- Genre string format: "Action | Drama | Thriller" (split on " | " during insertion)
- Date fields stored as SQLAlchemy `Date` type, converted from datetime strings

### Prefect Flow Execution

- Tasks have retries configured: 3 retries with 10-second delays
- Email task queries last 20 movies from database
- Email subject includes timestamp

### Environment Considerations

- **Timezone**: System must be set to America/Sao_Paulo for correct email timestamps
- **File locations**: Flow expects:
  - Scraper output: `movies_gratis.json`
  - Database: `dbs/movie_database.db`

## Data Flow

```
GratisTorrent Scraper → JSON file → SQLAlchemy ORM → SQLite Database → Email Report
                                                    ↓
                                              BigQuery (optional)
```

## Configuration Files

- `pyproject.toml`: Python dependencies (managed by UV)
- `ruff.toml`: Linting configuration
- `prefect.yaml`: Prefect deployment configuration
- `docker-compose.yaml`: Defines Prefect server and agent services
- `gratis_torrent/schema.json`: BigQuery table schema
