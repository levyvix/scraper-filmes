# GratisTorrent Scraper

Este repositório contém um scraper completo para o site [GratisTorrent](https://gratistorrent.com/).

Até novembro de 2025, o site **não possui proteção anti-robô** (diferente do ComandoTorrents), o que torna o processo de extração extremamente simples e estável.

## Tecnologias utilizadas

- **BeautifulSoup4** + **requests** – para parsing e download das páginas (o site é estático, sem JavaScript dinâmico)
- **Prefect** – orquestrador de workflows  
  Permite criar deploys automáticos que rodam em servidores externos.  
  O deploy atual está configurado para puxar diretamente a branch `main` do repositório remoto, facilitando testes em branches separadas sem afetar a execução em produção.
- **diskcache** – cache local em disco  
  Salva o HTML das páginas já baixadas, acelerando drasticamente o desenvolvimento e evitando requisições repetidas ao site.
- **Google BigQuery** – Data Warehouse  
  Banco de dados OLAP serverless no Google Cloud.  
  Possui um excelente free tier (1 TB de processamento/mês), mais do que suficiente para este projeto. Ótima escolha para aprender e trabalhar com ferramentas modernas de dados na nuvem.
- **Shared Utils** (`scrapers/utils/`) – Módulo compartilhado  
  Funções utilitárias e modelos de dados reutilizáveis entre diferentes scrapers, promovendo DRY (Don't Repeat Yourself) e facilitando manutenção.

## Objetivos de arquitetura

O código foi estruturado de forma **modular**, separando claramente as responsabilidades:

- Extração (scraping)
- Transformação dos dados
- Carregamento no BigQuery
- Orquestração com Prefect
- Cache local
- **Utilitários compartilhados** (`scrapers/utils/`) - Funções e modelos reutilizáveis

Essa separação facilita manutenção, testes e futuras evoluções do projeto.


---

**Status**: Ativo e rodando automaticamente em produção via Prefect Cloud.