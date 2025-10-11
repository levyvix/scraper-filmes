#!/bin/bash

# Script to deploy Prefect flows
# Usage: ./scripts/deploy_prefect.sh

set -e

echo "🚀 Deploying Prefect flows..."
echo ""

# Check if Prefect is configured
if ! uv run prefect config view | grep -q "PREFECT_API_URL"; then
    echo "⚠️  Prefect API URL not configured"
    echo "Please run: uv run prefect config set PREFECT_API_URL=<your-api-url>"
    echo "Or for local server: uv run prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api"
fi

# Deploy using prefect.yaml
cd /home/levi/projects/scraper-filmes

echo "📦 Deploying from config/prefect.yaml..."
uv run prefect --no-prompt deploy --prefect-file config/prefect.yaml --all

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Start a Prefect server (if not running): uv run prefect server start"
echo "2. Start a worker: uv run prefect worker start --pool default"
echo "3. Check deployments: uv run prefect deployment ls"
echo "4. Run manually: uv run prefect deployment run 'GratisTorrent Flow/gratis-torrent-scraper'"
