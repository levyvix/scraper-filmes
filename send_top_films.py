from filmes.send_email.send_email import send_email

import pandas as pd

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

engine = create_engine("sqlite:///data.db", echo=False)
session = Session(bind=engine)


def fetch_top_films():

    query = """
        SELECT * from data
        order by id DESC
        limit 20;
        """

    results = session.execute(query).fetchall()

    data = [row._asdict() for row in results]

    data = pd.DataFrame(data)

    session.close()

    return data


def send_top_films():

    data = fetch_top_films()

    send_email(message=data)


if __name__ == "__main__":

    send_top_films()
