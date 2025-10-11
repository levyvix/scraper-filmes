# 🧪 Suite de Testes

Suite completa de testes automatizados para o projeto Scraper de Filmes.

## 📋 O que é Testado

### 1. **Importações dos Módulos**
- Verifica se todos os módulos principais podem ser importados sem erros
- Testa: `extract.py`, `insert_to_database.py`, `prefect_flow_gratis.py`, `send_to_bq.py`

### 2. **Schema do Banco de Dados**
- Verifica criação das tabelas `movies` e `genres`
- Valida todos os campos obrigatórios
- Confirma que `genres` (não `genders`) está correto
- Valida campos `qualidade_video` (float) e `qualidade` (string)

### 3. **Validação Pydantic**
- Testa aceitação de dados válidos
- Verifica rejeição de IMDB > 10
- Verifica rejeição de ano < 1888
- Confirma tipos corretos (`qualidade_video` float, `qualidade` string)

### 4. **Inserção no Banco**
- Testa inserção de filmes no SQLite
- Verifica conversão de GB para MB
- Valida separação de gêneros em registros individuais
- Confirma todos os campos são salvos corretamente

### 5. **Deduplicação**
- Testa que filmes duplicados não são inseridos duas vezes
- Valida lógica de `titulo_dublado` + `date_updated`

### 6. **Carregamento de .env**
- Verifica que `python-dotenv` está funcionando
- Testa carregamento de variáveis de ambiente do arquivo `.env`

### 7. **Estrutura do Prefect Flow**
- Valida estrutura do flow principal
- Verifica todas as tasks estão definidas
- Confirma parâmetro `export_bq` existe

---

## 🚀 Como Executar

### Executar Todos os Testes

```bash
uv run python tests/test_suite.py
```

### Saída Esperada

```
============================================================
🧪 SUITE DE TESTES - SCRAPER DE FILMES
============================================================

============================================================
TEST: 1. Importações dos Módulos
============================================================
Testando importações...
  ✓ src.scrapers.gratis_torrent.extract
  ✓ src.database.insert_to_database
  ✓ src.flows.prefect_flow_gratis
  ✓ src.scrapers.gratis_torrent.send_to_bq
✅ PASSOU

...

============================================================
RESUMO DOS TESTES
============================================================
✅ Passou: 7
❌ Falhou: 0
📊 Total: 7

============================================================
🎉 TODOS OS TESTES PASSARAM!
============================================================
```

---

## ⏰ Execução Periódica

### Manualmente

Execute sempre que:
- Fizer mudanças no código
- Antes de fazer commits importantes
- Depois de atualizar dependências

### Com Cron (Linux/Mac)

Adicionar ao crontab para rodar diariamente às 8h:

```bash
crontab -e
```

Adicione a linha:

```cron
0 8 * * * cd /caminho/para/scraper-filmes && uv run python tests/test_suite.py >> tests/test_log.txt 2>&1
```

### Com GitHub Actions

Crie `.github/workflows/tests.yml`:

```yaml
name: Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 8 * * *'  # Diariamente às 8h

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      - name: Run tests
        run: uv run python tests/test_suite.py
```

---

## 🐛 Quando um Teste Falha

### 1. Ver Detalhes do Erro

O resumo mostrará qual teste falhou e o motivo:

```
============================================================
ERROS DETALHADOS
============================================================

4. Inserção no Banco:
  Esperado 2 filmes, encontrado 0
```

### 2. Verificar Logs

Se o teste falhou:
1. Leia a mensagem de erro cuidadosamente
2. Verifique se as dependências estão instaladas: `uv sync`
3. Verifique se algum arquivo foi modificado incorretamente
4. Execute o teste individual para debug

### 3. Executar Teste Individual

Para debugar um teste específico, edite `test_suite.py` e comente os outros:

```python
# runner.test("1. Importações dos Módulos", test_imports)
# runner.test("2. Schema do Banco de Dados", test_database_schema)
# runner.test("3. Validação Pydantic", test_pydantic_validation)
runner.test("4. Inserção no Banco", test_database_insertion)  # Apenas este
```

---

## 📝 Notas Importantes

- **Sem Rede**: Os testes não fazem scraping real (não precisam de internet)
- **Temporários**: Usa arquivos temporários (não afeta seu banco de dados)
- **Rápido**: Todos os testes rodam em ~2-3 segundos
- **Isolados**: Cada teste limpa seus dados após execução

---

## 🔧 Adicionar Novos Testes

Para adicionar um novo teste:

1. Crie uma função `test_nome_do_teste()` em `test_suite.py`
2. Use `print()` para mostrar progresso
3. Use `assert` para validar condições
4. Adicione ao runner no `main()`:

```python
runner.test("8. Meu Novo Teste", test_nome_do_teste)
```

Exemplo:

```python
def test_meu_recurso():
    """Testa meu novo recurso"""
    print("Testando meu recurso...")

    from src.meu_modulo import minha_funcao

    resultado = minha_funcao()
    assert resultado == "esperado", "Resultado incorreto"

    print("  ✓ Funcionou!")
```

---

## 📚 Recursos

- **Pytest**: Para testes mais avançados, considere usar `pytest`
- **Coverage**: Para ver cobertura de testes, use `coverage.py`
- **CI/CD**: Integre com GitHub Actions, GitLab CI, etc.
