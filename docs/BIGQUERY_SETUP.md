# Guia de Configuração do BigQuery

Este guia explica como configurar e testar a inserção de dados no BigQuery.

## Pré-requisitos

- Google Cloud SDK instalado ✓
- Biblioteca `google-cloud-bigquery` instalada ✓
- Criar um projeto ✓

## Opções de Autenticação

### Opção 1: Application Default Credentials (Recomendado)

Este método usa suas credenciais pessoais do Google Cloud:

```bash
# 1. Fazer login no Google Cloud
gcloud auth application-default login

# 2. Configurar o projeto
gcloud config set project <nome-do-projeto>

# 3. Testar a conexão
uv run python scripts/test_bigquery.py
```

### Opção 2: Service Account (Para Produção)

Use uma conta de serviço com arquivo JSON de credenciais:

```bash
# 1. Baixar o arquivo de credenciais do console do Google Cloud
# https://console.cloud.google.com/iam-admin/serviceaccounts

# 2. Configurar a variável de ambiente
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-credentials.json"

# 3. Testar a conexão
uv run python test_bigquery.py
```

## Testando a Integração

### 1. Teste de Conexão

```bash
# Executa verificações de credenciais e conexão
uv run python test_bigquery.py
```


## Estrutura do BigQuery

O script cria automaticamente:

### Dataset
- **Nome**: `movies_raw`
- **Localização**: US

### Tabelas

1. **filmes** (tabela principal)
   - Armazena todos os filmes únicos (deduplicado por link)

2. **stg_filmes** (tabela staging)
   - Tabela temporária para carregar novos dados
   - É truncada após cada merge

### Schema da Tabela

| Campo            | Tipo    | Modo     |
|------------------|---------|----------|
| titulo_dublado   | STRING  | REQUIRED |
| titulo_original  | STRING  | REQUIRED |
| imdb             | FLOAT   | NULLABLE |
| ano              | INTEGER | REQUIRED |
| genero           | STRING  | REQUIRED |
| tamanho          | STRING  | REQUIRED |
| duracao_minutos  | INTEGER | REQUIRED |
| qualidade_video  | FLOAT   | REQUIRED |
| qualidade        | STRING  | REQUIRED |
| dublado          | BOOLEAN | REQUIRED |
| sinopse          | STRING  | REQUIRED |
| link             | STRING  | REQUIRED |

## Processo de Importação

1. **Criar Dataset e Tabelas**: Se não existirem
2. **Load**: Carrega `movies_gratis.json` → `stg_filmes`
3. **Merge**: Insere apenas novos filmes (baseado no link)
4. **Truncate**: Limpa a tabela staging

## Verificando os Dados

### Via Console Web
1. Acesse: https://console.cloud.google.com/bigquery
2. Navegue até: `<projeto>` → `movies_raw` → `filmes`
3. Clique em "Query" e execute:
```sql
SELECT COUNT(*) as total_filmes FROM `<projeto>.movies_raw.filmes`
```

### Via CLI
```bash
# Contar filmes
bq query --use_legacy_sql=false \
  'SELECT COUNT(*) as total FROM `<projeto>.movies_raw.filmes`'

# Ver últimos 10 filmes
bq query --use_legacy_sql=false \
  'SELECT titulo_dublado, ano, imdb FROM `<projeto>.movies_raw.filmes` LIMIT 10'
```

## Troubleshooting

### Erro: "Your default credentials were not found"
**Solução**: Execute `gcloud auth application-default login`

### Erro: "Permission denied"
**Solução**: Verifique se você tem permissões no projeto:
```bash
gcloud projects get-iam-policy <projeto> --flatten="bindings[].members" --filter="bindings.members:user:$(gcloud config get-value account)"
```

### Erro: "Dataset not found"
**Solução**: O script cria automaticamente. Verifique se tem permissão `bigquery.datasets.create`

### Erro: "JSON file not found"
**Solução**: Execute o scraper primeiro:
```bash
uv run main.py
```

## Custos

- BigQuery tem free tier de 1TB de consultas/mês
- Armazenamento: primeiros 10GB são gratuitos
- Este projeto usa volumes bem abaixo do free tier