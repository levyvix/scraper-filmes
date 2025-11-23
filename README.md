# Scraper de Filmes

Sistema automatizado de scraping de filmes do site GratisTorrent/ComandoTorrents e exportação para BigQuery e orquestração com Prefect.

## 🚀 Início Rápido

### Instalação

Este projeto usa [uv](https://docs.astral.sh/uv/) para gerenciamento de dependências.

```bash
# Instalar apenas dependências principais (produção)
uv sync

# Instalar com dependências de desenvolvimento (testes, linting, type checking)
uv sync --group dev

# Instalar tudo (recomendado para desenvolvimento)
uv sync --all-groups
```

**Grupos de Dependências:**
- **main**: Dependências necessárias para executar os scrapers
- **dev**: Ferramentas de desenvolvimento (pytest, mypy, pre-commit, types-requests)

### Configurar Pre-commit Hooks (Desenvolvimento)

Pre-commit hooks garantem qualidade de código antes de cada commit:

```bash
# Instalar hooks (após uv sync --group dev)
uv run pre-commit install

# Executar manualmente em todos os arquivos
uv run pre-commit run --all-files

# Os hooks rodarão automaticamente em cada commit
```

**Hooks configurados:**
- Remoção de espaços em branco
- Formatação com Ruff
- Linting com Ruff
- Type checking com MyPy
- Validação de YAML/JSON/TOML

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
- ✅ Monitoramento e alertas de anomalias
- ✅ Type checking com MyPy (0 erros)

### Comando Torrents Scraper
- ✅ Scraping stealth com bypass de Cloudflare
- ✅ Cache em disco para otimização (DiskCache)
- ✅ Validação de dados com Pydantic
- ✅ Exportação para JSON local
- ✅ Parser robusto com tratamento de erros
- ✅ Extração aprimorada de ano do filme com fallbacks múltiplos

### Qualidade e Confiabilidade
- ✅ **209 testes unitários** com **85% de cobertura**
- ✅ **Type checking** com MyPy (configurado em pre-commit)
- ✅ **Linting e Formatação** com Ruff
- ✅ **Logging centralizado** com Loguru
- ✅ **Monitoramento de saúde** com alertas por email
- ✅ **Validação de env vars** com Pydantic Settings
- ✅ **Rate limiting** para evitar bloqueios
- ✅ **Data quality checks** automáticos


## 🔧 Melhorias Implementadas (Code Review)

Implementação completa de sugestões de código review focadas em qualidade e confiabilidade:

### Infraestrutura
- ✅ Consolidação de dependências (removido `requirements.txt`, mantém `pyproject.toml`)
- ✅ Organização de `.gitignore` com seções lógicas
- ✅ Correção do entrypoint em `prefect.yaml`

### Logging e Monitoramento
- ✅ **Logging centralizado** com Loguru em `scrapers/utils/logging_config.py`
- ✅ **Monitoramento de saúde** em `scrapers/utils/monitoring.py`
  - Detecção de anomalias (contagem baixa, falhas de load, taxa de sucesso)
  - Alertas por email automáticos
  - Integração com `send_mail.py`

### Qualidade de Código
- ✅ **Type checking** com MyPy (0 erros em 46 arquivos)
- ✅ **Pre-commit hooks** configurados com:
  - Formatação automática (Ruff)
  - Linting (Ruff)
  - Type checking (MyPy)
  - Validação de arquivos (YAML, JSON, TOML)

### Testes e Cobertura
- ✅ **209 testes unitários** passando
- ✅ **85% de cobertura de código**
- ✅ Pytest configurado em `pyproject.toml`
- ✅ Fixtures de teste atualizadas

### Parser Aprimorado
- ✅ Extração de ano em Comando Torrents com 3 estratégias de fallback:
  1. CSS selector direto
  2. Dados estruturados
  3. Busca de padrão 4 dígitos (1888-2100)

### Validação de Ambiente
- ✅ Validação de variáveis com Pydantic Settings
- ✅ Error handling robusto em `scrapers/utils/exceptions.py`
- ✅ Rate limiting em `scrapers/utils/rate_limiter.py`
- ✅ Data quality checks em `scrapers/utils/data_quality.py`

## 📂 Estrutura dos Scrapers

### 1. GratisTorrent (`run_gratis.py`)
Scraper completo com integração BigQuery e Prefect. Ideal para produção.

**Localização do módulo:** `scrapers/gratis_torrent/`

**Características:**
- Cliente HTTP customizado com retry
- Integração com BigQuery
- Orquestração Prefect
- Armazenamento SQLite local
- Utiliza `scrapers/utils` para funções comuns e modelos


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

### 3. Shared Utils (`scrapers/utils/`)
Módulo de utilitários compartilhados entre os scrapers com suporte a logging, monitoramento e validação.

**Localização do Módulo:** `scrapers/utils/`

**Componentes:**
- `parse_utils.py`: Funções auxiliares para limpeza e extração de texto
- `models.py`: Modelos de dados base (Pydantic) compartilhados
- `send_mail.py`: Utilitário para envio de notificações
- `logging_config.py`: Configuração centralizada de Loguru
- `monitoring.py`: Monitoramento de saúde e alertas de anomalias
- `exceptions.py`: Exceções customizadas para tratamento de erros
- `rate_limiter.py`: Decorator para rate limiting de requisições
- `data_quality.py`: Verificações de qualidade de dados


## 🧪 Testes e Validação

### Executar Testes
```bash
# Rodar todos os testes unitários
uv run pytest scrapers/tests/unit -v

# Rodar com relatório de cobertura
uv run pytest scrapers/tests --cov=scrapers --cov-report=html

# Rodar testes de integração
uv run pytest scrapers/tests/integration -v
```

### Type Checking
```bash
# Verificar tipos com MyPy
uv run mypy --ignore-missing-imports scrapers/

# MyPy também roda automaticamente em pre-commit
uv run pre-commit run mypy --all-files
```

### Linting e Formatação
```bash
# Verificar e corrigir com Ruff
uv run ruff check --fix scrapers/
uv run ruff format --line-length 120 scrapers/

# Executar todos os pre-commit hooks
uv run pre-commit run --all-files
```

## 📚 Documentação

- [BIGQUERY_SETUP.md](docs/BIGQUERY_SETUP.md) - Guia de configuração do BigQuery
- [PREFECT_DEPLOYMENT.md](docs/PREFECT_DEPLOYMENT.md) - Guia completo de deployment com Prefect

## 🛠️ Tecnologias

### Core
- **Python 3.11+**
- **UV** - Gerenciamento de dependências
- **Pydantic** - Validação de dados
- **Pydantic Settings** - Validação de variáveis de ambiente

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

### Logging, Monitoramento e Qualidade
- **Loguru** - Logging centralizado com rotação de arquivos
- **MyPy** - Type checking estático
- **Ruff** - Linting e formatação
- **Pytest** - Framework de testes
- **Pre-commit** - Git hooks para validação automática

## 📝 Licença

Este projeto é para fins educacionais.
