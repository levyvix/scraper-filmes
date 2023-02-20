from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.orm import sessionmaker, scoped_session, relationship

# import base class
from sqlalchemy.ext.declarative import declarative_base
from argparse import ArgumentParser
import json

engine = create_engine("sqlite:///movie_database.db", echo=True)

print(engine)


# def create_database():

#     with engine.connect() as conn:
#         conn.execute(
#             """CREATE TABLE IF NOT EXISTS movies
#             (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
#                 titulo_dublado TEXT UNIQUE NOT NULL,
#                 titulo TEXT,
#                 imdb REAL,
#                 ano INTEGER,
#                 genero TEXT,
#                 tamanho_mb REAL,
#                 duracao_min INTEGER,
#                 qualidade REAL,
#                 dublado BOOLEAN,
#                 sinopse TEXT,
#                 link TEXT)"""
#         )

# create orm database

Base = declarative_base()


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo_dublado = Column(String, unique=True)
    titulo_original = Column(String)
    imdb = Column(Float)
    ano = Column(Integer)
    genero = Column(String)
    tamanho_mb = Column(Float)
    duracao_minutos = Column(Integer)
    qualidade = Column(Float)
    dublado = Column(Boolean)
    sinopse = Column(String)
    link = Column(String)


def create_database():
    Base.metadata.create_all(engine)


# insert data into the database, if the data already exists, ignore it, use with context manager
def insert_to_database(json_string):
    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()

    data = json.loads(json_string)

    for movie in data:
        # check if the movie already exists
        if (
            session.query(Movie)
            .filter_by(titulo_dublado=movie["titulo_dublado"])
            .first()
        ):
            continue

        session.add(
            Movie(
                titulo_dublado=movie["titulo_dublado"],
                titulo_original=movie["titulo_original"],
                imdb=movie["imdb"],
                ano=movie["ano"],
                genero=movie["genero"],
                tamanho_mb=movie["tamanho_mb"],
                duracao_minutos=movie["duracao_minutos"],
                qualidade=movie["qualidade"],
                dublado=movie["dublado"],
                sinopse=movie["sinopse"],
                link=movie["link"],
            )
        )

    session.commit()
    session.close()


if __name__ == "__main__":

    # take the arguments
    parser = ArgumentParser()
    parser.add_argument("--data", help="data to insert into database (*.json)")
    args = parser.parse_args()

    with open(args.data, "r", encoding="utf-8") as f:
        data = f.read()

    create_database()
    insert_to_database(data)
