import datetime
import json

from sqlalchemy import Boolean, Column, Date, Float, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
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
    date_updated = Column(Date)
    link = Column(String)


# insert data into the database, if the data already exists, ignore it
def insert_to_database(json_path, engine):
    with Session(bind=engine) as sess:
        with open(json_path, "r", encoding="utf-8", errors="ignore") as json_file:
            data = json.load(json_file)

        for movie in data:
            movie = Movie(**movie)

            movie.date_updated = datetime.datetime.strptime(
                movie.date_updated, "%Y-%m-%d %H:%M:%S"
            ).date()
            # check if movie already exists
            if sess.query(Movie).filter_by(
                titulo_dublado=movie.titulo_dublado,
                date_updated=movie.date_updated,
            ).first():
                continue
            else:
                sess.add(movie)

        sess.commit()


def create_and_insert(json_f):
    # TODO: pass engine to function instead of calling inside

    engine = create_engine("sqlite:///movie_database.db", echo=False)

    Base.metadata.create_all(engine)

    insert_to_database(json_f, engine)


if __name__ == "__main__":
    create_and_insert("filmes.json")
