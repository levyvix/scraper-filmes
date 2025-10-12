#!/usr/bin/env python
"""Demonstração de problema de imports."""

print("=== Teste 1: Import relativo de arquivo na mesma pasta ===")
try:
    # Isso funciona APENAS quando rodado como módulo
    from src.scrapers.gratis_torrent.bigquery_client import load_movies_to_bigquery
    print("✅ Import absoluto funcionou (rodando como módulo ou com sys.path correto)")
except ModuleNotFoundError as e:
    print(f"❌ Import absoluto falhou: {e}")

print("\n=== Teste 2: Import relativo simples ===")
try:
    # Isso NÃO funciona porque não estamos no mesmo diretório
    from bigquery_client import load_movies_to_bigquery
    print("✅ Import relativo funcionou")
except ModuleNotFoundError as e:
    print(f"❌ Import relativo falhou: {e}")

print("\n=== sys.path atual ===")
import sys
for i, path in enumerate(sys.path[:5]):
    print(f"{i}: {path}")
