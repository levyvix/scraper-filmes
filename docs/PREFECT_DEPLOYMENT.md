# Prefect Deployment Guide

## Visão Geral

Este projeto usa Prefect para orquestrar o scraping de filmes do GratisTorrent.

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
