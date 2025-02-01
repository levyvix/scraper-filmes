from extract import main as extract
from send_to_bq import main as send_to_bq


def run_extract():
    extract()


def run_send_to_bq():
    send_to_bq()


def run_dag():
    run_extract()
    run_send_to_bq()


if __name__ == "__main__":
    run_dag()
