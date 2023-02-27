import scrapy
import logging
from datetime import datetime
import locale

try:
    locale.setlocale(locale.LC_ALL, "pt_BR")
except:
    locale.setlocale(locale.LC_ALL, "Portuguese_Brazil")

# stop scrap log
logging.getLogger("scrapy").propagate = False


class FilmesSpider(scrapy.Spider):
    name = "filmes"

    start_urls = ["https://comando.la/category/filmes/"]

    def parse(self, response):
        for div in response.xpath('//header[@class = "entry-header cf"]'):
            url = div.xpath(".//h2[1]/a/@href").extract_first()

            yield scrapy.Request(url=url, callback=self.parse_detail, meta={"url": url})

        # pega a próxima página
        next_page = response.xpath(
            "//html/body/div[1]/div[2]/div[1]/div[2]/div/a[7]/@href"
        ).extract_first()
        if next_page is not None:
            # yield scrapy.Request(response.urljoin(next_page), callback = self.parse)
            yield response.follow(next_page, callback=self.parse)

    def parse_detail(self, response):
        informacoes = response.xpath(
            "//html/body/div/div[2]/div[1]/article/div[2]/p[1]/text()"
        ).extract()

        # get release date (div.entry-byline cf > div.entry-date > a)
        date_updated = response.css(
            "div.entry-byline.cf > div.entry-date > a::text"
        ).extract_first()

        # string to date
        date_updated = datetime.strptime(date_updated, "%d de %B de %Y")

        # se nao tem espaço, entao tem informações
        infos = [i for i in informacoes if i not in ["\n", " ", "/10"]]
        # self.log(infos)
        # logging.info(infos)

        if "MKV" in infos[8]:
            del infos[8]

        titulo_dublado = infos[0]
        titulo = infos[1]

        try:
            imdb = response.xpath(
                "//html/body/div/div[2]/div[1]/article/div[2]/p[1]/a/text()"
            ).extract()[0]

            if str(imdb).startswith("20"):
                # not a imdb link, thats a year link
                imdb = infos[2]
                imdb = imdb.replace(":", "").strip()

        except Exception:
            imdb = infos[2]

        genero = infos[3]

        # if genero.startswith('/10'):
        #     genero = infos[4]

        tamanho = infos[8]
        duracao = infos[9]
        qualidade = infos[10]
        idioma = infos[6]
        link = response.meta["url"]

        ano = response.xpath(
            "//html/body/div/div[2]/div[1]/article/div[2]/p[1]/a/text()"
        ).extract()

        ano = ano[1] if len(ano) > 1 else ano[0]

        if "," in ano:
            # not a year link, thats a imdb link
            ano = None

        sinopse = response.xpath(
            "/html/body/div/div[2]/div[1]/article/div[2]/p[2]/text()"
        ).extract_first()

        if sinopse is None:  # se a sinopse não existir, pega a próxima
            sinopse = response.xpath(
                "/html/body/div/div[2]/div[1]/article/div[2]/p[3]/text()"
            ).extract_first()

        dublado = "Português" in idioma
        titulo_dublado = titulo_dublado.replace(":", "").strip()
        titulo = titulo.replace(":", "").strip()
        ano = ano.replace(":", "").strip()
        sinopse = sinopse.replace(":", "").strip()
        genero = genero.replace(":", "").strip()
        tamanho = GB_to_MB(tamanho.replace(":", "").strip().split(" | ")[0])
        duracao = split_duracao(duracao.replace(":", "").strip())
        qualidade = float(qualidade.replace(":", "").strip().replace(",", "."))

        yield {
            "titulo_dublado": titulo_dublado,
            "titulo_original": titulo,
            "imdb": float(imdb.replace(",", ".")) if "–" not in imdb else -1,
            "ano": int(ano) if ano is not None else -1,
            "genero": genero,
            "tamanho_mb": tamanho,
            "duracao_minutos": duracao,
            "qualidade": qualidade,
            "dublado": dublado,
            "sinopse": sinopse,
            "date_updated": date_updated,
            "link": link,
        }


def GB_to_MB(tamanho):
    if "GB" in tamanho:
        tamanho = tamanho.replace("GB", "").strip()
        tamanho = float(tamanho) * 1024
    else:
        tamanho = tamanho.replace("MB", "").strip()
        tamanho = float(tamanho)

    return tamanho


def split_duracao(duracao):

    if "|" in duracao:
        duracao = duracao.split("|")[0].strip()

    # convert to minutes (TEMPLATE: 1h 26 Min. to: 86)
    if "h" in duracao:
        duracao = duracao.replace("h", "").strip()
        duracao = duracao.replace("Min.", "").strip()
        duracao = duracao.split(" ")
        duracao = int(duracao[0]) * 60 + int(duracao[1])

    else:
        duracao = duracao.replace("Min.", "").strip()
        duracao = int(duracao)

    return duracao
