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
- **SQLite**: Base de dados para persistir as informações dos filmes em um banco de dados relacional.
- **Prefect**: Framework para agendar o script para rodar diariamente e enviar um email com os novos filmes adicionados ao banco de dados SQLite.

## Como rodar o projeto

- Clone o repositório
- Instale as dependências com o comando `pip install -r requirements.txt`
- Entre na pasta do projeto `filmes` e execute o comando `scrapy crawl filmes -O filmes.json`
- O arquivo `filmes.json` será gerado com os dados do site
- Se quiser colocar os dados em um banco de dados, execute o comando `python3 insert_to_database.py --data filmes.json`. Ele irá criar um arquivo `movie_database.db` com a tabela `movies` populada.


## Agendando o script para rodar diariamente

- Instale o Prefect com o comando `pip install prefect`
- Inicie o servidor prefect com o comando `prefect server start`
- Construa o deploy com o comando `prefect deployment build filmes/prefect_flow.py:comandola_filmes --name filmes_flow -q padrao --apply`
- Execute o agent com o comando `prefect agent start -q padrao`
- Execute o flow com o comando `prefect deployment run "Comando Flow/filmes_flow"`

### Agendar Diariamente
- Entre na UI do Prefect com o link: http://localhost:4200/
- Clique em Deployments
- Ache o flow `Comando Flow/filmes_flow` e clique nos 3 pontinhos e "Edit"
- Lá em baixo, em Schedule, você pode agendar o flow para rodar diariamente clicando em "Add".
- Salve as alterações e o flow será executado diariamente desde de que o servidor esteja ativo e o agent esteja rodando.


## Postagem sobre o projeto

[Web Scraping em um site de filmes online](https://medium.com/@levyvix/como-fazer-raspagem-de-dados-em-sites-com-scrapy-e-python-1cc315f301fb)

### TODO list
- [X] Enviar email diariamente sobre os "N" novos filmes adicionados por data de atualização. Usando Airflow ou Prefect
- [ ] Criar um corpo de email melhor, com os dados do filme, imagem e link para o site
- [ ] Obter informações sobre atores do filme, colocar em uma tabela separada e relacionar com a tabela de filmes
- [ ] Agendar o download de filmes remotamente para meu servidor local do Jellyfin
