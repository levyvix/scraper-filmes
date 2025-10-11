from typing import Optional
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
    titulo_dublado: str | None = None
    titulo_original: str | None = None
    imdb: float | None = Field(..., ge=0, le=10)
    ano: int | None = Field(..., ge=1888)
    genero: str | None = None
    tamanho: str | None = None
    duracao_minutos: int | None = Field(..., ge=1)
    qualidade_video: float | None = Field(..., ge=0, description="Video quality score (0-10)")
    qualidade: str | None = Field(..., description="Quality description (e.g., '1080p', '720p BluRay')")
    dublado: bool | None = None
    sinopse: str | None = None
    link: str | None = None


def extract_info(url: str) -> Optional[Movie]:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    info_text = soup.select_one("#informacoes > p")
    if not info_text:
        return None
    texto = info_text.text
    texto = re.sub(r": \n", ": ", texto)

    logger.debug(texto)

    # Extract data using regex patterns
    valores_extraidos = {}

    titulo_dublado_match = re.search(r"Baixar (.+) Torrent", texto)
    valores_extraidos["titulo_dublado"] = titulo_dublado_match.group(1).strip() if titulo_dublado_match else None

    titulo_original_match = re.search(r"Título Original:\s*(.+)\s*", texto)
    valores_extraidos["titulo_original"] = titulo_original_match.group(1).strip() if titulo_original_match else None

    imdb_match = re.search(r"Imdb:\s*(.+)\s*/", texto)
    valores_extraidos["imdb"] = imdb_match.group(1).strip() if imdb_match else None

    ano_match = re.search(r"Lançamento:\s*(\d{4})", texto)
    valores_extraidos["ano"] = ano_match.group(1).strip() if ano_match else None

    genero_match = re.search(r"Gêneros:\s*(.+)\s*Idioma:", texto, re.DOTALL)
    valores_extraidos["genero"] = genero_match.group(1).strip() if genero_match else None

    tamanho_match = re.search(r"Tamanho:\s*(.+)\s*GB", texto)
    valores_extraidos["tamanho"] = tamanho_match.group(1).strip() if tamanho_match else None

    duracao_match = re.search(r"Duração:\s*(\d+) Minutos", texto)
    valores_extraidos["duracao_minutos"] = duracao_match.group(1).strip() if duracao_match else None

    qualidade_video_match = re.search(r"Vídeo:\s*([0-9]+)\s*\|", texto)
    valores_extraidos["qualidade_video"] = qualidade_video_match.group(1).strip() if qualidade_video_match else None

    qualidade_match = re.search(r"Qualidade:\s*([0-9a-zA-Z |]+)", texto)
    valores_extraidos["qualidade"] = qualidade_match.group(1).strip() if qualidade_match else None

    sinopse = soup.select_one("#sinopse > p")

    if sinopse:
        texto_sinopse = sinopse.text

        texto_sinopse = texto_sinopse.split("Descrição")[-1].split(":")[-1].strip()
        valores_extraidos["sinopse"] = texto_sinopse

    return Movie(
        titulo_dublado=valores_extraidos["titulo_dublado"],
        titulo_original=valores_extraidos["titulo_original"],
        imdb=float(valores_extraidos["imdb"]) if valores_extraidos["imdb"] else None,
        ano=int(valores_extraidos["ano"]) if valores_extraidos["ano"] else None,
        genero=valores_extraidos["genero"].replace(" / ", ", ") if valores_extraidos["genero"] else None,
        tamanho=valores_extraidos["tamanho"],
        duracao_minutos=int(valores_extraidos["duracao_minutos"]) if valores_extraidos["duracao_minutos"] else None,
        qualidade_video=float(valores_extraidos["qualidade_video"]) if valores_extraidos["qualidade_video"] else None,
        qualidade=valores_extraidos["qualidade"],
        dublado="Português" in texto,
        sinopse=valores_extraidos["sinopse"],
        link=url,
    )


def main():
    website = "https://gratistorrent.com/lancamentos/"
    response = requests.get(website)
    soup = BeautifulSoup(response.text, "html.parser")

    elements = soup.select("#capas_pequenas > div > a")

    # Get unique movie links
    logger.info("Getting Movies...")
    links = []
    for element in elements:
        link = element["href"]
        if link not in links:
            links.append(link)

    # Extract movie information
    movies_list = []
    for link in links:
        movie = extract_info(link)
        print(movie)
        if movie:
            movies_list.append(movie.model_dump())

    # Save to JSON file
    with open("movies_gratis.json", "w", encoding="utf-8") as f:
        json.dump(movies_list, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
