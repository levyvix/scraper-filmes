from prefect import flow, task
from extract import main as extract
from send_to_bq import main as send_to_bq


@task
def run_extract():
    extract()


@task
def run_send_to_bq():
    send_to_bq()


@flow
def run_dag():
    run_extract()
    run_send_to_bq()


if __name__ == "__main__":
    run_dag()
