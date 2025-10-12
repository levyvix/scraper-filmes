# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A movie scraper project that automates scraping movies from the GratisTorrent website, with optional export to Google BigQuery. The project is built with Python and uses various libraries for web scraping, data validation, workflow orchestration, and data storage.

## Development Environment

### Prerequisites
- Python 3.11+
- UV for dependency management

### Setup
```bash
# Install dependencies
uv sync

# Set up environment variables (optional)
cp .env.example .env
# Edit .env with your specific configurations
```

## Common Commands

### Running the Project
```bash
# Run the main scraper
uv run main.py

# Run a specific test
uvx pytest tests/path/to/specific_test.py

# Run all tests
uvx pytest tests/

# Linting
uvx ruff check .

# Formatting
uvx ruff format --line-length 120

# Type checking
uvx mypy --ignore-missing-imports .
```

## Development Workflow

### Key Components
- **Scraper**: Located in `src/scrapers/gratis_torrent/scraper.py`
- **HTTP Client**: `src/scrapers/gratis_torrent/http_client.py`
- **BigQuery Integration**: `src/scrapers/gratis_torrent/bigquery_client.py`
- **Data Models**: `src/scrapers/gratis_torrent/models.py`

### Testing
- Use pytest for testing
- Test files are located in the `tests/` directory
- Run tests with `uvx pytest`

### Configuration
- Environment variables managed via `.env` file
- Project configuration in `pyproject.toml`
- Prefect workflow configuration in `prefect.yaml`

## Deployment

### Optional BigQuery Setup
Refer to `docs/BIGQUERY_SETUP.md` for detailed BigQuery configuration.

### Prefect Deployment
See `docs/PREFECT_DEPLOYMENT.md` for deployment instructions.

## Notes
- Project is for educational purposes
- Always validate and sanitize input data
- Respect website terms of service when scraping