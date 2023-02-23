import os
from prefect import flow, task
from filmes.insert_to_database import create_and_insert


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

    return os.path.abspath("filmes.json")


@task(
    name="Insert into database",
    log_prints=True,
    retries=3,
    retry_delay_seconds=10,
)
def insert(path):
    create_and_insert(path)


# @task(name="Send Email")
# def send():
#     # sql fetch last 10 movies
#     engine = create_engine("sqlite:///movie_database.db")

#     df = pd.read_sql_query("SELECT * FROM movies ORDER BY id DESC LIMIT 10", engine)

#     send_email(
#         df,
#         subject=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
#     )


@flow(name="Comando Flow", log_prints=True)
def comandola_filmes():
    print(os.getcwd())
    os.chdir("filmes")
    path = run_spider()
    os.chdir("..")
    os.chdir("dbs")
    insert(path)
    os.chdir("..")
    # send()


if __name__ == "__main__":
    comandola_filmes()
