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


Site utilizado: [comando torrents](https://comando.to/)


## Como rodar o projeto

- Clone o repositório
- Instale as dependências com o comando `pip install -r requirements.txt`
- Entre na pasta do projeto `filmes` e execute o comando `scrapy crawl filmes -o filmes.json`
- O arquivo `filmes.json` será gerado com os dados do site


