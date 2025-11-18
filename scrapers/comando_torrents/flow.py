import json
from pathlib import Path
from datetime import timedelta
from prefect import flow, task
from prefect.cache_policies import INPUTS, TASK_SOURCE
from scrapers.utils.logging_config import setup_logging
from scrapers.utils.models import Movie
from scrapers.comando_torrents.config import Config
from scrapers.comando_torrents.scraper import get_movie_links
from scrapers.comando_torrents.parser import parse_detail

# Initialize logging configuration
logger = setup_logging(level="INFO", log_file="comando_torrents.log")


@task(
    name="scrape-comando-movies",
    retries=2,
    retry_delay_seconds=30,
    cache_policy=INPUTS + TASK_SOURCE,
    cache_expiration=timedelta(hours=1),
    log_prints=True,
)
def scrape_movies_task(url_base: str) -> list[Movie]:
    logger.info(f"Fetching movie links from {url_base}")
    links = get_movie_links(url_base)

    if not links:
        logger.error("No movie links found. Please check the website or your connection.")
        return []

    logger.info(f"Found {len(links)} movie links. Starting to scrape...")

    list_movies: list[Movie] = []
    for index, link in enumerate(links, start=1):
        logger.info(f"Processing movie {index}/{len(links)}: {link}")

        movie = parse_detail(str(link))
        if movie:
            list_movies.append(movie)
            
    return list_movies


@task(name="save-comando-movies", log_prints=True)
def save_to_json_task(config: Config, list_movies: list[Movie]):
    json_path = Path(__file__).parent / config.JSON_FILE_NAME
    json_data = json.dumps(
        [movie.model_dump(mode="json") for movie in list_movies],
        indent=2,
        ensure_ascii=False,
    )
    json_path.write_text(json_data, encoding="utf-8")
    return json_path


@flow(name="comando-torrents-scraper", log_prints=True)
def comando_torrents_flow():
    """Main function to scrape movies and save to JSON."""
    config = Config()
    
    list_movies = scrape_movies_task(config.URL_BASE)

    if not list_movies:
        logger.error("No movies were successfully scraped.")
        return

    json_path = save_to_json_task(config, list_movies)

    logger.success(f"Saved {len(list_movies)} movies to {json_path}")
