import scrapy


class FilmesSpider(scrapy.Spider):
    name = 'filmes'

    start_urls = ['https://comando.to/category/filmes/']

    def parse(self, response):
        for div in response.xpath('//header[@class = "entry-header cf"]'):
            url = div.xpath(
                './/h2[1]/a/@href').extract_first()

            yield scrapy.Request(
                url=url,
                callback=self.parse_detail
            )

        next_page = response.xpath(
            '//html/body/div[1]/div[2]/div[1]/div[2]/div/a[7]/@href').extract_first()
        if next_page is not None:
            yield scrapy.Request(response.urljoin(next_page))

    def parse_detail(self, response):
        informacoes = response.xpath(
            '//html/body/div/div[2]/div[1]/article/div[2]/p[1]/text()').extract()

        # se nao tem espaço, entao tem informações
        infos = [i for i in informacoes if i not in ['\n', ' ', ': ']]
        self.log(infos)

        titulo = infos[1]
        imdb = infos[2]
        genero = infos[3]
        tamanho = infos[8]
        duracao = infos[9]
        qualidade = infos[10]

        ano = response.xpath(
            '//html/body/div/div[2]/div[1]/article/div[2]/p[1]/a/text()').extract_first()
        sinopse = response.xpath(
            '/html/body/div/div[2]/div[1]/article/div[2]/p[2]/text()').extract_first()

        if sinopse is None:  # se a sinopse não existir, pega a próxima
            sinopse = response.xpath(
                '/html/body/div/div[2]/div[1]/article/div[2]/p[3]/text()').extract_first()

        tem_dublado = response.xpath(  # se conseguir achar o texto, tem dublado
            '//strong[contains(text(), ":: DUAL ÁUDIO ::")]')

        dublado = bool(tem_dublado)

        # nome de hoje
        yield {
            'nome': titulo,
            'imdb': imdb,
            'ano': ano,
            'genero': genero,
            'tamanho': tamanho,
            'duracao': duracao,
            'qualidade': qualidade,
            'dublado': dublado,
            'sinopse': sinopse
        }
