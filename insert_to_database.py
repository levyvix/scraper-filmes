import datetime
import json

from sqlalchemy import Boolean, Column, Date, Float, Integer, String, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship

Base = declarative_base()


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    titulo_dublado = Column(String)
    titulo_original = Column(String)
    imdb = Column(Float)
    ano = Column(Integer)
    # genero = Column(String)
    tamanho_mb = Column(Float)
    duracao_minutos = Column(Integer)
    qualidade = Column(Float)
    dublado = Column(Boolean)
    sinopse = Column(String)
    date_updated = Column(Date)
    link = Column(String)

class Gender(Base):

    __tablename__ = "genders"
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    movie_id = Column(Integer, ForeignKey('movies.id'))
    gender = Column(String)


# insert data into the database, if the data already exists, ignore it
def insert_to_database(json_path, engine):
    """
    Pega o caminho do arquivo json e insere os dados no banco de dados SQLite


    Args:
        json_path (str): caminho do arquivo json
        engine (sqlalchemy.engine.base.Engine): engine do banco de dados


    Examples:
        >>> insert_to_database("filmes.json", engine)
    """
    with Session(bind=engine) as sess:
        with open(json_path, "r", encoding="utf-8", errors="ignore") as json_file:
            data = json.load(json_file)

        for movie in data:
            movie_entity = Movie(
                titulo_dublado=movie["titulo_dublado"],
                titulo_original=movie["titulo_original"],
                imdb=movie["imdb"],
                ano=movie["ano"],
                # genero=movie["genero"],
                tamanho_mb=movie["tamanho_mb"],
                duracao_minutos=movie["duracao_minutos"],
                qualidade=movie["qualidade"],
                dublado=movie["dublado"],
                sinopse=movie["sinopse"],
                date_updated=movie["date_updated"],
                link=movie["link"],
            )

            list_of_genders = movie['genero'].split(" | ")

            movie_entity.date_updated = datetime.datetime.strptime(
                movie_entity.date_updated, "%Y-%m-%d %H:%M:%S"
            ).date()
            # check if movie already exists
            if sess.query(Movie).filter_by(
                titulo_dublado=movie_entity.titulo_dublado,
                date_updated=movie_entity.date_updated,
            ).first():
                continue
            else:
                sess.add(movie_entity)

                # add genders
                for g in list_of_genders:
                    gender = Gender(
                        movie_id=sess.query(Movie).filter_by(
                            titulo_dublado=movie_entity.titulo_dublado,
                            date_updated=movie_entity.date_updated,
                        ).first().id,
                        gender=g.strip(),
                    )
                    
                    sess.add(gender)


        sess.commit()


def create_and_insert(json_f, engine):
    """
    create the database and insert the data into it, if the database already exists, ignore it

    Args:
        json_f (str): path to the json file
        engine (sqlalchemy.engine.base.Engine): engine of the database

    Examples:
        >>> create_and_insert("filmes.json", engine)
    """
    # engine = create_engine("sqlite:///movie_database.db", echo=False)

    Base.metadata.create_all(engine)

    insert_to_database(json_f, engine)


if __name__ == "__main__":
    engine = create_engine("sqlite:///dbs/movie_database.db", echo=False)

    create_and_insert("filmes/filmes.json", engine)
