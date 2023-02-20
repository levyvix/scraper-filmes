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
- Link


Site utilizado: [Comando Torrents](https://comando.la/)


## Tecnologias 

- **Scrapy**: Usando este framework para realizar as chamadas HTTP, tratanto e carregando os dados em uma base json.
- **SQLAlchemy**: Usando este ORM para criar a tabela de filmes e persistir os dados.
- **SQLite**: Base de dados para persistir as informações dos filmes.

## Como rodar o projeto

- Clone o repositório
- Instale as dependências com o comando `pip install -r requirements.txt`
- Entre na pasta do projeto `filmes` e execute o comando `scrapy crawl filmes -O filmes.json`
- O arquivo `filmes.json` será gerado com os dados do site
- Se quiser colocar os dados em um banco de dados, execute o comando `python3 insert_to_database.py --data filmes.json`. Ele irá criar um arquivo `movie_database.db` com a tabela `movies` populada.


## Postagem sobre o projeto

[Web Scraping em um site de filmes online](https://medium.com/@levyvix/como-fazer-raspagem-de-dados-em-sites-com-scrapy-e-python-1cc315f301fb)

### TODO list
- [ ] Pegar imagem do filme
- [ ] Obter informações sobre atores do filme, colocar em uma tabela separada e relacionar com a tabela de filmes
- [ ] Enviar email diariamente sobre os "N" novos filmes adicionados. Usando Airflow ou Prefect
- [ ] Agendar o download de filmes remotamente para meu servidor local do Jellyfin
