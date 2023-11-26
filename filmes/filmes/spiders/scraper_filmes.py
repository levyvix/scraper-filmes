import logging
from pprint import pprint
import re
import scrapy
import dateparser
import dataclasses


@dataclasses.dataclass
class Movie:
    titulo_dublado: str
    titulo_original: str
    imdb: float
    ano: int
    genero: str
    tamanho_mb: float
    duracao_minutos: int
    qualidade: float
    dublado: bool
    sinopse: str
    date_updated: str
    link: str


# stop scrap log
logging.getLogger("scrapy").propagate = False


class FilmesSpider(scrapy.Spider):
    name = "filmes"

    start_urls = ["https://comando.la/category/filmes/"]

    def parse(self, response):
        # pega lista de cards
        for div in response.xpath('//header[@class = "entry-header cf"]'):
            # pega link do card
            url = div.xpath(".//h2[1]/a/@href").extract_first()

            # manda para o parse_detail
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
        date_updated = dateparser.parse(date_updated, languages=["pt"])

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

            if imdb is None or imdb == "???":
                imdb = -1

            elif str(imdb).startswith("20"):
                # not a imdb link, thats a year link
                imdb = infos[2]
                imdb = imdb.replace(":", "").strip()

        except Exception:
            imdb = infos[2]

        genero = infos[3]

        tamanho = infos[8]
        duracao = infos[9]

        qualidade = infos[10]
        idioma = infos[6]

        if duracao is not None and "GB" in duracao:
            duracao = infos[10]
            tamanho = infos[9]
            qualidade = infos[11]


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

        pat = r"(\d+\.\d+)"  # regex para pegar o tamanho do filme
        try:
            tamanho = re.findall(pat, tamanho)[0]  # pega o tamanho minimo
        except Exception:
            tamanho = 0

        dublado = "Português" in idioma
        titulo_dublado = titulo_dublado.replace(":", "").strip()
        titulo = titulo.replace(":", "").strip()
        ano = int(ano.replace(":", "").strip()) if ano is not None else -1
        sinopse = sinopse.replace(":", "").strip()
        genero = genero.replace(":", "").strip()
        tamanho = GB_to_MB(tamanho)
        duracao = split_duracao(duracao.replace(":", "").strip())
        qualidade = float(qualidade.replace(":", "").strip().replace(",", "."))


        if isinstance(imdb, str) and imdb is not None:
            if "–" not in imdb:
                imdb = float(imdb.replace(",", "."))
            else:
                imdb = -1

        movie = Movie(
            titulo_dublado=titulo_dublado,
            titulo_original=titulo,
            imdb=imdb,
            ano=ano,
            genero=genero,
            tamanho_mb=tamanho,
            duracao_minutos=duracao,
            qualidade=qualidade,
            dublado=dublado,
            sinopse=sinopse,
            date_updated=date_updated,
            link=link,
        )

        yield {
            "titulo_dublado": movie.titulo_dublado,
            "titulo_original": movie.titulo_original,
            "imdb": movie.imdb,
            "ano": movie.ano,
            "genero": movie.genero,
            "tamanho_mb": movie.tamanho_mb,
            "duracao_minutos": movie.duracao_minutos,
            "qualidade": movie.qualidade,
            "dublado": movie.dublado,
            "sinopse": movie.sinopse,
            "date_updated": movie.date_updated,
            "link": movie.link,
        }


def GB_to_MB(tamanho: str) -> float:
    """
    Converte o tamanho de GB para MB

    Args:
        tamanho (str): tamanho do filme em GB

    Returns:
        float: tamanho do filme em MB

    Examples:
        >>> GB_to_MB('2.45 GB')
        2560.0
    """

    if isinstance(tamanho, int):
        return tamanho

    if "GB" in tamanho:
        tamanho = tamanho.replace("GB", "").strip()
        tamanho = float(tamanho) * 1024
    else:
        tamanho = tamanho.replace("MB", "").strip()
        tamanho = float(tamanho)

    return tamanho


def split_duracao(duracao: str) -> int:
    """
    - Pega somente a primeira duração do filme
    - Converte a duração para minutos

    Args:
        duracao (str): duração do filme

    Returns:
        int: duração do filme em minutos

    Examples:
        >>> split_duracao('1h 30 Min. | 1h 40 Min.')
        90
    """

    if "|" in duracao:
        duracao = duracao.split("|")[0].strip()

    if "h" in duracao:
        duracao = duracao.replace("h", "").strip()
        duracao = duracao.replace("Min.", "").strip()
        duracao = duracao.split(" ")
        duracao = int(duracao[0]) * 60 + int(duracao[1])

    else:
        duracao = duracao.replace("Min.", "").strip()
        duracao = int(duracao)

    return duracao
