from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.orm import Session

# import base class
from sqlalchemy.ext.declarative import declarative_base
import json

engine = create_engine("sqlite:///movie_database.db", echo=False)

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
    link = Column(String)


# insert data into the database, if the data already exists, ignore it
def insert_to_database(json_path):
    with Session(bind=engine) as sess:
        with open(json_path, "r", encoding="utf-8", errors="ignore") as json_file:
            data = json.load(json_file)

        for movie in data:
            movie = Movie(**movie)
            # check if movie already exists
            if sess.query(Movie).filter_by(titulo_dublado=movie.titulo_dublado).first():
                continue
            else:
                sess.add(movie)

        sess.commit()


def create_and_insert(json):
    Base.metadata.create_all(engine)

    insert_to_database(json)


if __name__ == "__main__":
    create_and_insert("filmes.json")
