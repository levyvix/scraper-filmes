# Por que não consigo importar de um script na mesma pasta?

## O Problema

Quando você roda um script Python diretamente, você encontra 3 problemas principais:

### 1. **Imports Relativos com Ponto (`.`) Falham**

```python
# Em bigquery_client.py
from .config import Config  # ❌ FALHA quando rodado como script

# Error: ImportError: attempted relative import with no known parent package
```

**Por quê?** Imports relativos (`.`) só funcionam quando o arquivo é parte de um **pacote** (importado como módulo).

### 2. **sys.path aponta para o diretório do script, não do projeto**

Quando você roda:
```bash
python src/scrapers/gratis_torrent/flow.py
```

O Python adiciona `src/scrapers/gratis_torrent/` ao `sys.path`, não a raiz do projeto!

```python
sys.path[0] = '/home/levi/projects/scraper-filmes/src/scrapers/gratis_torrent'
# Não é: '/home/levi/projects/scraper-filmes'
```

Por isso `from src.scrapers...` não funciona - `src` não está no path!

### 3. **Você não pode importar arquivos da mesma pasta se eles usam imports relativos**

```python
# Em flow.py
from bigquery_client import load_movies_to_bigquery  # Parece certo?

# Mas bigquery_client.py contém:
from .config import Config  # ❌ EXPLODE!
```

## Soluções

### ✅ Solução 1: Rodar como módulo (recomendado)

```bash
# Usa -m para rodar como módulo, não como script
python -m src.scrapers.gratis_torrent.flow
```

Isso faz o Python:
- Adicionar a raiz do projeto ao sys.path
- Tratar o arquivo como parte de um pacote (imports relativos funcionam)

### ✅ Solução 2: Ajustar sys.path no início do script

```python
# No início do flow.py
import sys
from pathlib import Path

# Adicionar raiz do projeto ao sys.path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Agora pode usar imports absolutos
from src.scrapers.gratis_torrent.bigquery_client import load_movies_to_bigquery
```

### ✅ Solução 3: Converter todos os imports relativos em absolutos

```python
# Antes (em bigquery_client.py):
from .config import Config  # Import relativo

# Depois:
from src.scrapers.gratis_torrent.config import Config  # Import absoluto
```

Então ajustar sys.path quando necessário.

## O que fizemos no flow.py

Implementamos uma solução híbrida que funciona em ambos os casos:

```python
# Support both module and script execution
try:
    # Tenta import absoluto (funciona como módulo)
    from src.scrapers.gratis_torrent.bigquery_client import load_movies_to_bigquery
except ModuleNotFoundError:
    # Se falhar, ajusta sys.path e tenta novamente (funciona como script)
    import sys
    from pathlib import Path
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))
    from src.scrapers.gratis_torrent.bigquery_client import load_movies_to_bigquery
```

## Resumo Visual

```
# Rodando como SCRIPT (python flow.py)
/home/user/project/src/scrapers/gratis_torrent/flow.py
                    └─ sys.path[0] está AQUI ❌
                    └─ 'src' não está no path!

# Rodando como MÓDULO (python -m src.scrapers.gratis_torrent.flow)
/home/user/project/
└─ sys.path[0] está AQUI ✅
   └─ 'src' está no path!
```

## Regra de Ouro

**Use `-m` sempre que possível para rodar código que faz parte de um pacote!**

```bash
# ✅ Recomendado
python -m src.scrapers.gratis_torrent.flow

# ⚠️  Funciona mas requer ajuste de sys.path
python src/scrapers/gratis_torrent/flow.py
```
