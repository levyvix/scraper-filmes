from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.orm import sessionmaker, scoped_session, relationship

# import base class
from sqlalchemy.ext.declarative import declarative_base
import json

engine = create_engine("sqlite:///movie_database.db", echo=True)

print(engine)

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


# insert data into the database, if the data already exists, ignore it
def insert_to_database(json_path):
    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()

    with open(json_path, "r", encoding="utf-8", errors="ignore") as json_file:
        data = json.load(json_file)

    for movie in data:
        movie = Movie(**movie)
        # check if movie already exists
        if session.query(Movie).filter_by(titulo_dublado=movie.titulo_dublado).first():
            continue
        else:
            session.add(movie)

    session.commit()
    session.close()


def create_and_insert(json):

    create_database()
    insert_to_database(json)


if __name__ == "__main__":
    create_and_insert("filmes.json")
