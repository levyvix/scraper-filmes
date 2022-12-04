import scrapy
import logging


class FilmesSpider(scrapy.Spider):
    name = 'filmes'

    start_urls = ['https://comando.la/category/filmes/']

    def parse(self, response):
        for div in response.xpath('//header[@class = "entry-header cf"]'):
            url = div.xpath(
                './/h2[1]/a/@href').extract_first()

            yield scrapy.Request(
                url=url,
                callback=self.parse_detail,
                meta = {'url': url}
            )

        # pega a próxima página
        next_page = response.xpath(
            '//html/body/div[1]/div[2]/div[1]/div[2]/div/a[7]/@href').extract_first()
        if next_page is not None:
            # yield scrapy.Request(response.urljoin(next_page), callback = self.parse)
            yield response.follow(next_page, callback=self.parse)

    def parse_detail(self, response):
        informacoes = response.xpath(
            '//html/body/div/div[2]/div[1]/article/div[2]/p[1]/text()').extract()

        # se nao tem espaço, entao tem informações
        infos = [i for i in informacoes if i not in ['\n', ' ', '/10']]
        # self.log(infos)
        logging.info(infos)

        if 'MKV' in infos[8]:
            del infos[8]

        titulo_dublado = infos[0]
        titulo = infos[1]

        try: #tenta achar o imdb com o link
            imdb = response.xpath(
            '//html/body/div/div[2]/div[1]/article/div[2]/p[1]/a/text()').extract()[0]

            if str(imdb).startswith('20'):
                # not a imdb link, thats a year link
                imdb = infos[2]
                imdb = imdb.replace(':', '').strip()

        except:
            imdb = infos[2]
            

        genero = infos[3]

        # if genero.startswith('/10'):
        #     genero = infos[4]
        
        tamanho = infos[8]
        duracao = infos[9]
        qualidade = infos[10]
        link = response.meta['url']

        ano = response.xpath(
            '//html/body/div/div[2]/div[1]/article/div[2]/p[1]/a/text()').extract()

        if len(ano) > 1:
            ano = ano[1]
        else:
            ano = ano[0]

        
        if ',' in ano:
            # not a year link, thats a imdb link
            ano = None

        # if
        sinopse = response.xpath(
            '/html/body/div/div[2]/div[1]/article/div[2]/p[2]/text()').extract_first()

        if sinopse is None:  # se a sinopse não existir, pega a próxima
            sinopse = response.xpath(
                '/html/body/div/div[2]/div[1]/article/div[2]/p[3]/text()').extract_first()

        tem_dublado = response.xpath(  # se conseguir achar o texto, tem dublado
            '//strong[contains(text(), ":: DUAL ÁUDIO ::")]')

        dublado = bool(tem_dublado)

        
        titulo_dublado = titulo_dublado.replace(':', '').strip()
        titulo = titulo.replace(':', '').strip()
        ano = ano.replace(':', '').strip()
        sinopse = sinopse.replace(':', '').strip()
        genero = genero.replace(':', '').strip()
        tamanho = tamanho.replace(':', '').strip()
        duracao = duracao.replace(':', '').strip()
        qualidade = qualidade.replace(':', '').strip()

        yield {
            'titulo_dublado': titulo_dublado,
            'titulo_original': titulo,
            'imdb': imdb,
            'ano': ano,
            'genero': genero,
            'tamanho': tamanho,
            'duracao': duracao,
            'qualidade': qualidade,
            'dublado': dublado,
            'sinopse': sinopse,
            'link':link
        }
