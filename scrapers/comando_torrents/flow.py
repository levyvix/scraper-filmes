import json
from pathlib import Path
from datetime import timedelta
from prefect import flow, task
from prefect.cache_policies import INPUTS
from scrapers.utils.logging_config import setup_logging
from scrapers.utils.models import Movie
from scrapers.comando_torrents.config import ComandoTorrentsConfig
from scrapers.comando_torrents.scraper import get_movie_links
from scrapers.comando_torrents.parser import parse_detail
from loguru import logger

# Initialize logging configuration
setup_logging(level="INFO", log_file="comando_torrents.log")


@task(
    name="scrape-comando-movies",
    retries=2,
    retry_delay_seconds=30,
    cache_policy=INPUTS,
    cache_expiration=timedelta(hours=1),
    log_prints=True,
)
def scrape_movies_task(url_base: str) -> list[Movie]:
    from scrapers.utils.data_quality import DataQualityChecker

    logger.info(f"Fetching movie links from {url_base}")
    links = get_movie_links(url_base)

    if not links:
        logger.error(
            "No movie links found. Please check the website or your connection."
        )
        return []

    logger.info(f"Found {len(links)} movie links. Starting to scrape...")

    list_movies: list[Movie] = []
    quality_checker = DataQualityChecker(min_fields_filled=0.7)
    failed_count = 0

    for index, link in enumerate(links, start=1):
        logger.info(f"Processing movie {index}/{len(links)}: {link}")

        movie = parse_detail(str(link))
        if movie:
            # Validate movie quality before adding to list
            if quality_checker.check_movie(movie):
                list_movies.append(movie)
            else:
                logger.warning(f"Movie {link} failed quality checks")
                failed_count += 1
        else:
            failed_count += 1

    logger.info(
        f"Successfully scraped {len(list_movies)} movies. "
        f"Failed: {failed_count} out of {len(links)}"
    )

    # Log quality report
    if list_movies:
        report = quality_checker.check_batch(list_movies)
        logger.info(
            f"Quality Report: {report['pass_rate']:.1%} pass rate "
            f"({report['passed_quality']}/{report['total_movies']} movies)"
        )

    return list_movies


@task(name="save-comando-movies", log_prints=True)
def save_to_json_task(config: ComandoTorrentsConfig, list_movies: list[Movie]) -> Path:
    json_path = Path(__file__).parent / config.JSON_FILE_NAME
    json_data = json.dumps(
        [movie.model_dump(mode="json") for movie in list_movies],
        indent=2,
        ensure_ascii=False,
    )
    json_path.write_text(json_data, encoding="utf-8")
    return json_path


@flow(name="comando-torrents-scraper", log_prints=True)
def comando_torrents_flow() -> None:
    """Main function to scrape movies and save to JSON."""
    config = ComandoTorrentsConfig()

    list_movies = scrape_movies_task(config.URL_BASE)

    if not list_movies:
        logger.error("No movies were successfully scraped.")
        return

    json_path = save_to_json_task(config, list_movies)

    logger.success(f"Saved {len(list_movies)} movies to {json_path}")
