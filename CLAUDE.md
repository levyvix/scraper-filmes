# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A production-grade web scraping and data pipeline project for collecting movie data from the GratisTorrent website, using Python, Prefect, and Google BigQuery.

## Development Commands

### Setup
```bash
# Install dependencies
uv sync

# Run type checking
uvx mypy --ignore-missing-imports .

# Lint the code
uvx ruff check .

# Format the code
uvx ruff format --line-length 120
```

### Testing
```bash
# Run integration test suite
uv run python tests/test_suite.py

# Run specific test module (example)
uv run python tests/scrapers/gratis_torrent/test_parser.py
```

### Prefect Deployment
```bash
# Start Prefect server
prefect server start

# Create default work pool
prefect work-pool create defaultp --set-as-default

# Deploy workflow
prefect deploy -n default

# Start worker
prefect worker start --pool defaultp
```

## Key Architecture Notes

### Data Pipeline
- Uses Prefect for workflow orchestration
- Scrapes GratisTorrent website
- Validates data with Pydantic models
- Stores data directly in Google BigQuery
- 24-hour disk caching to reduce redundant requests

### Core Modules
- `src/scrapers/gratis_torrent/`
  - `scraper.py`: High-level scraping workflow
  - `parser.py`: HTML parsing logic
  - `http_client.py`: Web request handling
  - `models.py`: Pydantic data validation
  - `bigquery_client.py`: BigQuery data operations

### Environment Configuration
- Uses `.env` file for configuration
- Critical environment variables:
  - `GCP_PROJECT_ID`: Google Cloud project ID
  - Ensure these are set before running deployment scripts

## Deployment Targets
1. Local development
2. Prefect server with scheduled jobs
3. Docker containerization (currently under refactoring)

## Ongoing Migration
- Currently transitioning from SQLite to direct BigQuery pipeline
- Old database modules have been removed
- Update tests to reflect new architecture

## Contribution Guidelines
- Always run type checking, linting, and formatting before committing
- Ensure all tests pass after making changes
- Update documentation if architecture changes
- Be mindful of the ongoing migration and architectural simplification

## Troubleshooting
- If tests fail, verify environment setup
- Check BigQuery credentials and project configuration
- Ensure UV dependencies are synchronized