import datetime
import json

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    Float,
    Integer,
    String,
    create_engine,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

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
    qualidade_video = Column(Float)  # Video quality score (0-10)
    qualidade = Column(String)  # Quality description (e.g., '1080p', '720p BluRay')
    dublado = Column(Boolean)
    sinopse = Column(String)
    date_updated = Column(Date)
    link = Column(String)


class Genre(Base):
    __tablename__ = "genres"
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    movie_id = Column(Integer, ForeignKey("movies.id"))
    genre = Column(String)


# insert data into the database, if the data already exists, ignore it
def insert_to_database(json_path, engine):
    """
    Insert movie data from JSON file into SQLite database.
    Skips movies that already exist (based on title and date).

    Args:
        json_path (str): Path to JSON file containing movie data
        engine (sqlalchemy.engine.base.Engine): Database engine

    Examples:
        >>> insert_to_database("filmes.json", engine)
    """
    with Session(bind=engine) as sess:
        with open(json_path, "r", encoding="utf-8", errors="ignore") as json_file:
            data = json.load(json_file)

        for movie in data:
            # Convert tamanho from GB string to MB float
            if "tamanho" in movie and "tamanho_mb" not in movie:
                tamanho_str = movie["tamanho"]
                movie["tamanho_mb"] = float(tamanho_str) * 1024

            # Add date_updated if missing
            if "date_updated" not in movie:
                movie["date_updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Parse date_updated to date object
            date_updated = datetime.datetime.strptime(movie["date_updated"], "%Y-%m-%d %H:%M:%S").date()

            # Check if movie already exists
            existing_movie = (
                sess.query(Movie)
                .filter_by(
                    titulo_dublado=movie["titulo_dublado"],
                    date_updated=date_updated,
                )
                .first()
            )

            if existing_movie:
                continue

            # Create new movie entity
            movie_entity = Movie(
                titulo_dublado=movie["titulo_dublado"],
                titulo_original=movie["titulo_original"],
                imdb=movie["imdb"],
                ano=movie["ano"],
                tamanho_mb=movie["tamanho_mb"],
                duracao_minutos=movie["duracao_minutos"],
                qualidade_video=float(movie["qualidade_video"]),
                qualidade=movie["qualidade"],
                dublado=movie["dublado"],
                sinopse=movie["sinopse"],
                date_updated=date_updated,
                link=movie["link"],
            )
            sess.add(movie_entity)
            sess.flush()  # Get the movie ID immediately

            # Parse genres and create genre entries
            genero_str = movie["genero"]
            if " | " in genero_str:
                list_of_genres = genero_str.split(" | ")
            else:
                list_of_genres = genero_str.split(", ")

            for genre_name in list_of_genres:
                genre = Genre(
                    movie_id=movie_entity.id,
                    genre=genre_name.strip(),
                )
                sess.add(genre)

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

    create_and_insert("filmes/f.json", engine)
