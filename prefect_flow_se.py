import os
from datetime import datetime

import pandas as pd
from prefect import flow, task

# from prefect.tasks import task_input_hash
from sqlalchemy import create_engine

from insert_to_database import create_and_insert
from filmes.send_email.send_email import send_email


@task(
    name="Run the spider",
    log_prints=True,
    retries=3,
    retry_delay_seconds=10,
    # cache_key_fn=task_input_hash,
    # cache_expiration=timedelta(minutes=10),
)
def run_spider():
    try:
        os.remove("filmes.json")
    except FileNotFoundError:
        print("filmes.json already deleted")

    # scrapy crawl filmes_spider -O filmes.json

    os.system("scrapy crawl filmes -O filmes.json")


@task(
    name="Insert into database",
    log_prints=True,
    retries=3,
    retry_delay_seconds=10,
)
def insert(path, engine):
    create_and_insert(path, engine)


@task(name="Send Email")
def send(engine):
    # sql fetch last 20 movies
    # engine = create_engine("sqlite:///dbs/movie_database.db")

    df = pd.read_sql_query(
        """
        SELECT titulo_dublado, group_concat(gender, ', ') as genero, tamanho_mb, duracao_minutos, 
        qualidade, dublado, date_updated, sinopse, link
        FROM movies 
        JOIN genders ON movies.id = genders.movie_id
        GROUP BY movies.id
        ORDER BY date_updated DESC
        LIMIT 20
        """,
        engine,
    )

    send_email(
        df,
        subject=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    )


@flow(name="Comando Flow", log_prints=True)
def comandola_filmes():
    # create engine
    engine = create_engine("sqlite:///dbs/movie_database.db")

    # print(os.getcwd())
    os.chdir("filmes")
    run_spider()
    os.chdir("../dbs")
    # os.chdir("dbs")
    insert("../filmes/filmes.json", engine)
    os.chdir("..")
    send(engine)


if __name__ == "__main__":
    comandola_filmes()
