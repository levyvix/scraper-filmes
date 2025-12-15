# Prefect Deployment Guide

## Overview

This project uses Prefect to orchestrate the GratisTorrent movie scraping pipeline with BigQuery integration.

## Prerequisites for Deployment

Before deploying, ensure you have:

- **GCP Project ID**: Your Google Cloud project ID (e.g., `galvanic-flame-384620`)
- **GCP Service Account**: With BigQuery Editor/Admin role
- **SSH Key**: For GitHub SSH-based repository cloning
- **Prefect Setup**: Local server or Prefect Cloud account

## Environment Variables and Credentials

The deployed flow requires two environment variables passed via `job_variables` in `prefect.yaml`:

### Configuration Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `GCP_PROJECT_ID` | Yes | Google Cloud project ID | `galvanic-flame-384620` |
| `GCP_CREDENTIALS_METHOD` | Yes | Credential method: `ADC` or `FILE` | `ADC` |
| `GCP_CREDENTIALS_PATH` | No | Path to service account JSON (if METHOD=FILE) | `/etc/gcp/service-account.json` |

### Credential Methods

#### Option A: Application Default Credentials (ADC) - Recommended for Cloud

Use ADC for cloud deployments with workload identity, gcloud CLI, or GCP service account.

**When to use**:
- Running on Google Cloud (Compute Engine, Cloud Run, GKE)
- Using workload identity federation
- Local development with `gcloud auth application-default login`

**Setup**:

```bash
# On local machine or GCP VM with gcloud installed
gcloud auth application-default login

# Or configure workload identity on GKE/Cloud Run
# (handled by platform automatically)
```

**prefect.yaml configuration**:

```yaml
job_variables:
  GCP_PROJECT_ID: "your-project-id"
  GCP_CREDENTIALS_METHOD: "ADC"
```

**Advantages**:
- No credentials file to manage
- Automatic credential discovery
- Best for cloud deployments
- GCP-native credential chain

**Security**:
- Credentials not stored in code
- Follows GCP security best practices

#### Option B: Service Account JSON File - For On-Premise/Local

Use FILE method for local Prefect servers or on-premise deployments.

**When to use**:
- Local Prefect server + worker setup
- On-premise deployment
- CI/CD with external service account

**Setup**:

1. Create or use existing service account:

```bash
# Create a service account in GCP console or via gcloud
gcloud iam service-accounts create prefect-scraper \
  --display-name="Prefect Scraper Service Account"

# Grant BigQuery Admin role
gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:prefect-scraper@your-project-id.iam.gserviceaccount.com" \
  --role="roles/bigquery.admin"
```

2. Download JSON key file:

```bash
gcloud iam service-accounts keys create \
  /path/to/service-account.json \
  --iam-account=prefect-scraper@your-project-id.iam.gserviceaccount.com
```

3. Copy to worker machine and set permissions:

```bash
# Place file where worker can access it
cp /path/to/service-account.json /etc/gcp/service-account.json

# Restrict permissions
chmod 600 /etc/gcp/service-account.json
```

4. Configure `prefect.yaml`:

```yaml
job_variables:
  GCP_PROJECT_ID: "your-project-id"
  GCP_CREDENTIALS_METHOD: "FILE"
  GCP_CREDENTIALS_PATH: "/etc/gcp/service-account.json"
```

**Advantages**:
- Works without cloud infrastructure
- Simple for local testing

**Security**:
- Protect JSON file with strict permissions (600)
- Store file outside code repository
- Rotate keys periodically
- Use dedicated service account (not your personal account)

#### Option C: Prefect Cloud Secrets (Cloud-Only)

For Prefect Cloud deployments, store secrets securely in Prefect.

**Setup** (Prefect Cloud):

1. Create secret in Prefect Cloud UI:
   - Blocks → Create Block → JSON
   - Paste your service account JSON
   - Name: `gcp-credentials`

2. Reference in code (optional, for advanced scenarios):

```python
from prefect.context import get_secrets

secrets = get_secrets()
credentials = secrets["gcp-credentials"]
```

## SSH Key Setup for Git Clone

The deployment uses SSH to clone the repository. Set up SSH keys before deploying:

### Generate SSH Key (if needed)

```bash
# Generate ED25519 key (recommended, more secure)
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N ""

# Or use RSA (older systems)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
```

### Add SSH Key to GitHub

1. Copy your public key:

```bash
cat ~/.ssh/id_ed25519.pub  # or id_rsa.pub
```

2. Go to GitHub → Settings → SSH and GPG keys → New SSH key
3. Paste the public key
4. Add as deploy key to the repository (if using deploy keys)

### Verify SSH Connection

```bash
# Test SSH connection to GitHub
git ls-remote git@github.com:levyvix/scraper-filmes.git main

# Should output: <commit-hash>	refs/heads/main
```

### For Prefect Worker Machines

If running Prefect on a different machine:

1. Copy SSH key to worker machine:

```bash
scp ~/.ssh/id_ed25519 worker-user@worker-host:~/.ssh/
ssh worker-user@worker-host 'chmod 600 ~/.ssh/id_ed25519'
```

2. Or add SSH key to SSH agent:

```bash
ssh-agent bash
ssh-add ~/.ssh/id_ed25519
# Start Prefect worker in same shell
uv run prefect worker start --pool defaultp
```

### For GitHub Actions (CI/CD)

Add SSH key as a secret:

1. Go to GitHub repo → Settings → Secrets and variables → Actions
2. Create new secret: `SSH_PRIVATE_KEY` with your private key content
3. Use in workflow:

```yaml
- name: Deploy Prefect Flow
  env:
    SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
  run: |
    mkdir -p ~/.ssh
    echo "$SSH_PRIVATE_KEY" > ~/.ssh/id_ed25519
    chmod 600 ~/.ssh/id_ed25519
    ssh-keyscan github.com >> ~/.ssh/known_hosts
    uv run prefect deploy -n gratis-torrent
```

## Deployment Validation Checklist

Before going live, validate the deployment:

### Pre-Deployment Checks

- [ ] GCP project ID is correct in `prefect.yaml`
- [ ] Service account has BigQuery Admin role (if using FILE method)
- [ ] Credential file exists and readable (if using FILE method)
- [ ] SSH key is set up and GitHub connectivity works
- [ ] Prefect server is running (`uv run prefect server start`)

### Deployment Steps

1. **Validate configuration**:

```bash
# Check prefect.yaml is valid
uv run prefect config view

# Verify git clone will work
git ls-remote git@github.com:levyvix/scraper-filmes.git main
```

2. **Deploy the flow**:

```bash
uv run prefect deploy -n gratis-torrent
```

3. **Verify deployment**:

```bash
# List deployments
uv run prefect deployment ls

# Inspect deployment
uv run prefect deployment inspect 'gratis-torrent'
```

### Post-Deployment Validation

1. **Check credentials are loaded**:

```bash
# Manual test run
uv run prefect deployment run 'gratis-torrent'

# Check logs in Prefect UI for:
# "Loading GCP credentials using method: ADC"
# "Successfully loaded Application Default Credentials"
```

2. **Verify environment variables**:

```bash
# In Prefect UI, check deployment details
# job_variables section should show:
# GCP_PROJECT_ID: "your-project-id"
# GCP_CREDENTIALS_METHOD: "ADC"
```

3. **Test BigQuery connectivity**:

```bash
# Run the flow and monitor logs
uv run prefect deployment run 'gratis-torrent'

# Check that:
# - Git clone succeeds
# - Credentials load successfully
# - BigQuery dataset/tables are created
# - Data is inserted into staging table
```

### Troubleshooting

#### Git Clone Fails

```
Error: SSH key not found or permission denied
```

**Solution**:
- Verify SSH key is in `~/.ssh/`
- Check GitHub has your public key
- Test with: `git ls-remote git@github.com:levyvix/scraper-filmes.git`
- Add known_hosts: `ssh-keyscan github.com >> ~/.ssh/known_hosts`

#### Credentials Fail to Load

```
Error: Failed to load Application Default Credentials
```

**Solutions**:
- If using ADC: Run `gcloud auth application-default login`
- If using FILE: Verify path in `GCP_CREDENTIALS_PATH` exists and is readable
- Check file permissions: `ls -l /path/to/service-account.json` should show 600
- Verify service account JSON is valid

#### BigQuery Connection Fails

```
Error: 403 Forbidden - Permission Denied
```

**Solutions**:
- Verify service account has BigQuery Admin role
- Check project ID is correct
- Verify credentials are for the right GCP project
- Test locally: `uv run python -c "from scrapers.gratis_torrent.bigquery_client import get_client; get_client()"`

## Configuração do Deployment

### Comandos Essenciais (Ordem Recomendada)

**IMPORTANTE**: Estes comandos são necessários para configurar o Prefect corretamente pela primeira vez:

```bash
# 1. Iniciar o servidor Prefect (em um terminal separado)
uv run prefect server start

# 2. Criar o work pool padrão
uv run prefect work-pool create defaultp --set-as-default

# 3. Fazer o deploy do flow
uv run prefect deploy -n gratis-torrent

# 4. Iniciar o worker (em outro terminal)
uv run prefect worker start --pool defaultp
```

> **Nota**: Os passos 1 e 4 precisam rodar em terminais separados, pois são processos contínuos.

### Detalhamento dos Passos

### 1. Iniciar o Prefect Server (Local)

```bash
uv run prefect server start
```

O servidor ficará disponível em: http://127.0.0.1:4200

### 2. Criar o Work Pool

```bash
uv run prefect work-pool create defaultp --set-as-default
```

Este comando cria o work pool que gerenciará a execução dos flows.

### 3. Deploy do Flow

```bash
# Usando o deployment configurado no prefect.yaml
uv run prefect deploy -n gratis-torrent
```


### 4. Iniciar um Worker

```bash
uv run prefect worker start --pool defaultp
```

## Agendamento

O flow está configurado para rodar:
- **Horário**: 02:00 (2h da manhã)
- **Frequência**: Diariamente
- **Timezone**: America/Sao_Paulo
- **Cron**: `0 2 * * *`

Para alterar o agendamento, edite `config/prefect.yaml`:

```yaml
schedules:
  - cron: '0 2 * * *'  # Min Hora Dia Mês DiaSemana
    timezone: America/Sao_Paulo
    active: true
```

### Exemplos de Cron:

- `0 */6 * * *` - A cada 6 horas
- `0 0 * * 0` - Todo domingo à meia-noite
- `30 14 * * 1-5` - Segunda a sexta às 14:30

## Comandos Úteis

### Listar Deployments

```bash
uv run prefect deployment ls
```

### Ver Detalhes de um Deployment

```bash
uv run prefect deployment inspect 'GratisTorrent Flow/gratis-torrent-scraper'
```

### Executar Manualmente

```bash
uv run prefect deployment run 'GratisTorrent Flow/gratis-torrent-scraper'
```

### Ver Runs Recentes

```bash
uv run prefect flow-run ls --limit 10
```

### Pausar/Ativar Schedule

```bash
# Pausar
uv run prefect deployment pause 'GratisTorrent Flow/gratis-torrent-scraper'

# Ativar
uv run prefect deployment resume 'GratisTorrent Flow/gratis-torrent-scraper'
```

### Deletar Deployment

```bash
uv run prefect deployment delete 'GratisTorrent Flow/gratis-torrent-scraper'
```

## Estrutura do Flow

O flow `gratis_torrent_flow` executa:

1. **run_gratis_scraper**: Executa o scraper e gera `movies_gratis.json`
2. **insert_movies**: Insere os filmes no banco SQLite
3. **get_stats**: Mostra estatísticas dos filmes
4. **export_to_bigquery**: (Opcional) Exporta para BigQuery

## Parâmetros

O flow aceita o parâmetro `export_bq` (boolean):

```bash
# Com export para BigQuery
uv run prefect deployment run 'GratisTorrent Flow/gratis-torrent-scraper' --param export_bq=true

# Sem export para BigQuery
uv run prefect deployment run 'GratisTorrent Flow/gratis-torrent-scraper' --param export_bq=false
```

## Monitoramento

Acesse o Prefect UI em http://127.0.0.1:4200 para:
- Ver logs em tempo real
- Monitorar execuções
- Visualizar o histórico
- Gerenciar agendamentos

## Troubleshooting

### Worker não está pegando tasks

Certifique-se de que:
1. O Prefect server está rodando
2. O worker está conectado ao work pool correto (`default`)
3. O deployment foi criado corretamente

### Flow falha ao executar

Verifique:
1. Dependências instaladas: `uv sync`
2. Caminhos corretos no código
3. Logs no Prefect UI ou terminal do worker

### Alterar Work Pool

Se precisar usar um work pool diferente:

```bash
# Criar novo work pool
uv run prefect work-pool create my-pool --type process

# Atualizar prefect.yaml
# work_pool:
#   name: my-pool

# Iniciar worker
uv run prefect worker start --pool my-pool
```

## Prefect Cloud (Opcional)

Para usar Prefect Cloud em vez de local:

1. Criar conta em https://app.prefect.cloud
2. Criar API key
3. Configurar:

```bash
uv run prefect cloud login --key YOUR_API_KEY
```

4. Deploy normalmente com `uv run prefect deploy -n gratis-torrent`
