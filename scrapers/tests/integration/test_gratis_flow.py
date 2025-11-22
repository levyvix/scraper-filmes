from scrapers.gratis_torrent.flow import (
    gratis_torrent_flow,
    scrape_movies_task,
    load_to_bigquery_task,
)


def test_flow_structure():
    """Tests the structure of the Prefect flow."""
    assert gratis_torrent_flow.name == "gratis-torrent-scraper"


def test_task_structure():
    """Tests the structure of the Prefect tasks."""
    assert scrape_movies_task.name == "scrape-movies"
    assert load_to_bigquery_task.name == "load-to-bigquery"

    assert scrape_movies_task.retries == 2
    assert load_to_bigquery_task.retries == 3
