# Web Scraping em um site de filmes online


Este projeto foi criado com o intuito de criar um script para raspar um site de filmes online e conseguir as seguintes informações:

- Nome do filme
- Ano de lançamento
- Nota IMDB
- Gênero
- Tamanho
- Duração
- Qualidade de vídeo
- Se tem a opção dublado
- Sinopse


Site utilizado: [comando torrents](https://comando.la/)


## Tecnologias 

- Scrapy: Usando este framework para realizar as chamadas HTTP, tratanto e carregando os dados em uma base.
- Scrapyd: Interface web para rodar as `spiders`.
- SQLite: Base de dados para persistir as informações dos filmes.

## Como rodar o projeto

- Clone o repositório
- Instale as dependências com o comando `pip install -r requirements.txt`
- Entre na pasta do projeto `filmes` e execute o comando `scrapy crawl filmes -o filmes.json`
- O arquivo `filmes.json` será gerado com os dados do site


## Postagem sobre o projeto

[Web Scraping em um site de filmes online](https://medium.com/@levyvix/como-fazer-raspagem-de-dados-em-sites-com-scrapy-e-python-1cc315f301fb)

### TODO list
- Pegar imagem do filme
- enviar email diariamente sobre os novos filmes adicionados
- agendar o download de filmes remotamente para meu servidor local
