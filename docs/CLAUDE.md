# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Core Development Commands

### Project Setup
```bash
# Install dependencies
uv sync

# Run linting
ruff check .

# Run tests
uv run python tests/test_suite.py
```

### Workflow Execution
```bash
# Run complete scraping and database workflow
uv run src/flows/prefect_flow_gratis.py

# Run scraper manually
uv run src/scrapers/gratis_torrent/extract.py

# Run BigQuery export (optional)
uv run src/scrapers/gratis_torrent/send_to_bq.py
```

### Prefect Workflow Management
```bash
# Start Prefect server
prefect server start

# Create work pool
prefect work-pool create defaultp

# Build and apply deployment
prefect deploy -n default

# Start worker
prefect worker start --pool defaultp
```

## Key Architecture Components

### Scraping Pipeline
- **Source**: GratisTorrent website
- **Tools**: BeautifulSoup, Requests
- **Validation**: Pydantic `Movie` model
- **Output**: `movies_gratis.json`

### Database Layer
- **Database**: SQLite (`dbs/movie_database.db`)
- **ORM**: SQLAlchemy
- **Models**:
  - `movies`: Movie metadata
  - `genres`: Genre relationships
- **Features**: Deduplication, automatic timestamp

### Workflow Orchestration
- **Tool**: Prefect
- **Flow**: `gratis_torrent_flow()` in `src/flows/prefect_flow_gratis.py`
- **Tasks**:
  1. Web Scraping
  2. SQLite Insertion
  3. Statistics Generation
  4. Optional BigQuery Export

## Environment Requirements
- Python 3.11+
- UV for dependency management
- Prefect for workflow orchestration
- Optional: Google Cloud SDK for BigQuery

## Deployment Options
- Local execution
- Prefect scheduled deployment
- Docker containerization

## Development Notes
- Always run linting after code changes
- Use UV for all dependency management
- Ensure .env is configured for BigQuery export