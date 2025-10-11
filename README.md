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

### 2. Configurar Variáveis de Ambiente (Opcional)

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env com suas configurações (especialmente GCP_PROJECT_ID para BigQuery)
# O arquivo .env é carregado automaticamente pelos scripts
```

### 3. Executar o Scraper

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

## 🔄 Como Funciona o Pipeline

### Visão Geral do Fluxo de Dados

O projeto implementa um pipeline completo de ETL (Extract, Transform, Load) orquestrado pelo Prefect:

```
Web Scraping → Validação → SQLite → BigQuery (opcional)
                                  ↓
                            Estatísticas
```

### 1. **Extração (Web Scraping)** - `src/scrapers/gratis_torrent/extract.py`

**Task Prefect**: `run_gratis_scraper()`

O scraper realiza as seguintes operações:

1. **Coleta de Links**: Acessa `https://gratistorrent.com/filmes/` e extrai todos os links de filmes da página inicial usando BeautifulSoup
2. **Extração de Dados**: Para cada filme, acessa a página individual e extrai informações usando regex:
   - Título dublado e original
   - Nota IMDB, ano de lançamento
   - Gêneros, duração em minutos
   - Qualidade do vídeo, tamanho do arquivo
   - Sinopse e link do torrent
3. **Validação com Pydantic**: Cada filme é validado usando o model `Movie` que garante:
   - IMDB entre 0-10
   - Ano >= 1888 (primeiro filme da história)
   - Duração >= 1 minuto
4. **Saída**: Gera o arquivo `movies_gratis.json` com todos os filmes validados

**Configuração de Retry**: 3 tentativas com 10 segundos de delay entre falhas

### 2. **Transformação e Carga no SQLite** - `src/database/insert_to_database.py`

**Task Prefect**: `insert_movies()`

O processo de inserção no banco de dados:

1. **Criação de Tabelas** (se não existirem):
   - `movies`: Armazena os dados principais dos filmes
   - `genres`: Armazena os gêneros (relacionamento N:N com filmes)

2. **Transformações**:
   - Converte tamanho de GB (string) para MB (float)
   - Adiciona data de atualização (`date_updated`) automaticamente
   - Separa gêneros em registros individuais na tabela `genres`

3. **Deduplicação Inteligente**:
   - Verifica se o filme já existe usando `titulo_dublado` + `date_updated`
   - Ignora filmes duplicados automaticamente
   - Permite que o mesmo filme seja inserido novamente em datas diferentes

4. **Transação Atômica**: Todas as inserções são feitas em uma única transação (commit ao final)

**Configuração de Retry**: 3 tentativas com 10 segundos de delay entre falhas

### 3. **Estatísticas** - Task `get_stats()`

Gera e exibe estatísticas do banco de dados:
- Total de filmes cadastrados
- Total de gêneros únicos
- Média das notas IMDB
- Data da última atualização

### 4. **Exportação para BigQuery (Opcional)** - `src/scrapers/gratis_torrent/send_to_bq.py`

**Task Prefect**: `export_to_bigquery()` - Executada apenas se `export_bq=True`

#### Processo de ETL no BigQuery:

1. **Criação da Infraestrutura**:
   - Dataset: `movies_raw`
   - Tabela staging: `stg_filmes` (temporária)
   - Tabela final: `filmes` (produção)

2. **Load para Staging**:
   - Carrega o arquivo `movies_gratis.json` na tabela `stg_filmes`
   - Usa schema definido em `schema.json` para validação
   - Formato: NEWLINE_DELIMITED_JSON

3. **Merge (Upsert)**:
   ```sql
   MERGE INTO filmes AS target
   USING stg_filmes AS source
   ON target.link = source.link
   WHEN NOT MATCHED THEN INSERT ...
   ```
   - Compara filmes por `link` (chave única)
   - Insere apenas filmes novos (evita duplicação)
   - Retorna número de linhas afetadas

4. **Limpeza**:
   - Trunca a tabela `stg_filmes` após o merge
   - Prepara para a próxima execução

**Vantagens da Abordagem Staging**:
- ✅ Separação entre dados temporários e produção
- ✅ Validação antes de afetar dados finais
- ✅ Rollback fácil em caso de problemas
- ✅ Auditoria do processo de carga

### 🎯 Orquestração com Prefect

**Flow Principal**: `gratis_torrent_flow()` - `src/flows/prefect_flow_gratis.py`

#### Execução das Tasks:

```python
# 1. Scraping
run_gratis_scraper()
    ↓
# 2. Inserção no SQLite
insert_movies(json_path, engine)
    ↓
# 3. Estatísticas
get_stats(engine)
    ↓
# 4. BigQuery (condicional)
if export_bq:
    export_to_bigquery()
```

#### Recursos do Prefect:

1. **Retry Automático**: Tasks com falha são reexecutadas automaticamente (3x)
2. **Logging**: Todos os prints são capturados nos logs do Prefect
3. **Monitoramento**: UI web em `http://127.0.0.1:4200` mostra:
   - Status de cada task em tempo real
   - Logs completos de execução
   - Histórico de runs
   - Métricas de performance
4. **Agendamento**: Execução automática via cron (configurável em `config/prefect.yaml`)
5. **Parâmetros**: Flow aceita `export_bq` para controlar exportação ao BigQuery

#### Configuração do Deployment:

Para executar o flow automaticamente (agendado), é necessário:

1. **Prefect Server**: Interface web e API (`uv run prefect server start`)
2. **Work Pool**: Gerencia a fila de execução (`uv run prefect work-pool create defaultp`)
3. **Deployment**: Configuração do agendamento (`uv run prefect deploy -n default`)
4. **Worker**: Processo que executa as tasks (`uv run prefect worker start --pool defaultp`)

Veja [PREFECT_DEPLOYMENT.md](docs/PREFECT_DEPLOYMENT.md) para instruções detalhadas.

### 🎛️ Modos de Execução

#### 1. Execução Local Simples (Sem Agendamento)
```bash
uv run src/flows/prefect_flow_gratis.py
```
- Executa o flow imediatamente
- Não requer servidor Prefect
- Ideal para desenvolvimento e testes

#### 2. Execução via Deployment (Com Agendamento)
```bash
# Configurar infraestrutura (uma vez)
uv run prefect server start
uv run prefect work-pool create defaultp --set-as-default
uv run prefect deploy -n default

# Iniciar worker (mantém rodando)
uv run prefect worker start --pool defaultp
```
- Flow roda automaticamente no horário agendado
- Monitoramento via UI web
- Ideal para produção

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
# 1. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env e configurar GCP_PROJECT_ID

# 2. Autenticar com Google Cloud
gcloud auth application-default login

# 3. Testar conexão com BigQuery
uv run scripts/test_bigquery.py

# 4. Enviar dados para BigQuery
uv run src/scrapers/gratis_torrent/send_to_bq.py

# Para configuração completa, veja docs/BIGQUERY_SETUP.md
```

**Nota:** O script `send_to_bq.py` carrega automaticamente o arquivo `.env` usando `python-dotenv`.

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
- [PREFECT_DEPLOYMENT.md](docs/PREFECT_DEPLOYMENT.md) - Guia completo de deployment com Prefect

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
