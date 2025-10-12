#!/usr/bin/env python
"""Teste de imports locais dentro do diretório gratis_torrent."""

print("=== Rodando de dentro de src/scrapers/gratis_torrent/ ===\n")

print("Teste 1: Import de arquivo na MESMA pasta (import relativo)")
try:
    from bigquery_client import load_movies_to_bigquery
    print("✅ Consegui importar bigquery_client (arquivo na mesma pasta)")
except ModuleNotFoundError as e:
    print(f"❌ Falhou: {e}")

print("\nTeste 2: Import absoluto do projeto (from src...)")
try:
    from src.scrapers.gratis_torrent.bigquery_client import load_movies_to_bigquery
    print("✅ Consegui importar com caminho absoluto")
except ModuleNotFoundError as e:
    print(f"❌ Falhou: {e}")
    print("   Isso falha porque 'src' não está no sys.path!")

print("\n=== sys.path (primeiros 3 caminhos) ===")
import sys
for i, path in enumerate(sys.path[:3]):
    print(f"{i}: {path}")

print(f"\n📁 Diretório atual: {sys.path[0]}")
