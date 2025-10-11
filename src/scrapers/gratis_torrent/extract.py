import requests
from bs4 import BeautifulSoup
import json
import re
from pydantic import BaseModel, Field
from rich import print
from loguru import logger
import sys

logger.remove()
logger.add(sys.stderr, level="WARNING")


class Movie(BaseModel):
    titulo_dublado: str
    titulo_original: str
    imdb: float | None = Field(..., ge=0, le=10)
    ano: int = Field(..., ge=1888)
    genero: str
    tamanho: str
    duracao_minutos: int = Field(..., ge=1)
    qualidade_video: float = Field(..., ge=0)
    qualidade: str
    dublado: bool
    sinopse: str
    link: str


def extract_info(url: str) -> Movie:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    info_text = soup.select_one("#informacoes > p")
    if not info_text:
        return None
    texto = info_text.text
    texto = re.sub(r": \n", ": ", texto)

    logger.debug(texto)

    padroes = {
        "titulo_dublado": re.search(r"Baixar (.+) Torrent", texto),
        "titulo_original": re.search(r"Título Original:\s*(.+)\s*", texto),
        "imdb": re.search(r"Imdb:\s*(.+)\s*/", texto),
        "ano": re.search(r"Lançamento:\s*(\d{4})", texto),
        "genero": re.search(r"Gêneros:\s*(.+)\s*Idioma:", texto, re.DOTALL),
        "tamanho": re.search(r"Tamanho:\s*(.+)\s*GB", texto),
        "duracao_minutos": re.search(r"Duração:\s*(\d+) Minutos", texto),
        "qualidade_video": re.search(r"Vídeo:\s*([0-9]+)\s*\|", texto),
        "qualidade": re.search(r"Qualidade:\s*([0-9a-zA-Z |]+)", texto),
    }

    valores_extraidos = {chave: padrao.group(1).strip() if padrao else None for chave, padrao in padroes.items()}

    sinopse = soup.select_one("#sinopse > p")

    if sinopse:
        texto_sinopse = sinopse.text

        texto_sinopse = texto_sinopse.split("Descrição")[-1].split(":")[-1].strip()
        valores_extraidos["sinopse"] = texto_sinopse

    return Movie(
        titulo_dublado=valores_extraidos["titulo_dublado"],
        titulo_original=valores_extraidos["titulo_original"],
        imdb=float(valores_extraidos["imdb"]) if valores_extraidos["imdb"] else None,
        ano=int(valores_extraidos["ano"]),
        genero=valores_extraidos["genero"].replace(" / ", ", ") if valores_extraidos["genero"] else "",
        tamanho=valores_extraidos["tamanho"],
        duracao_minutos=int(valores_extraidos["duracao_minutos"]),
        qualidade_video=float(valores_extraidos["qualidade_video"]),
        qualidade=valores_extraidos["qualidade"],
        dublado="Português" in texto,
        sinopse=valores_extraidos["sinopse"],
        link=url,
    )


def main():
    website = "https://gratistorrent.com/filmes/"
    response = requests.get(website)
    soup = BeautifulSoup(response.text, "html.parser")

    elements = soup.select("#capas_pequenas > div > a")

    movies_list = []
    logger.info("Getting Movies...")
    links = [ele["href"] for ele in elements]
    for link in set(links):
        movie = extract_info(link)
        print(movie)
        if movie:
            movies_list.append(movie.model_dump())

    with open("movies_gratis.json", "w", encoding="utf-8") as f:
        json.dump(movies_list, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
