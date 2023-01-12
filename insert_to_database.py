from sqlalchemy import create_engine
from argparse import ArgumentParser
import json

engine = create_engine('sqlite:///data.db', echo=False)
# create cursor


# def create_cursor():
#     return engine.connect()


def create_database():

    engine.execute(
        """CREATE TABLE IF NOT EXISTS data (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            titulo_dublado TEXT UNIQUE NOT NULL,
            titulo TEXT, 
            imdb TEXT, 
            ano INTEGER,
            genero TEXT,
            tamanho TEXT,
            duracao TEXT,
            qualidade TEXT,
            dublado BOOLEAN,
            sinopse TEXT,
            link TEXT)""")


# insert json into database and ignore duplicates
def insert_to_database(json_string):
    # read json
    data = json.loads(json_string)

    # cursor = create_cursor()
    for item in data:
        try:
            engine.execute(
                """INSERT OR IGNORE INTO data (titulo_dublado, titulo, imdb, ano, genero, tamanho, duracao, qualidade, dublado, sinopse, link) 
                VALUES (:titulo_dublado, :titulo_original, :imdb, :ano, :genero, :tamanho, :duracao, :qualidade, :dublado, :sinopse, :link)""",
                item)
        except Exception as e:
            print(e)
            print('Error inserting data into database')


if __name__ == '__main__':

    # take the arguments
    parser = ArgumentParser()
    parser.add_argument('--data', help='data to insert into database (*.json)')
    args = parser.parse_args()

    with open(args.data, 'r', encoding='utf-8') as f:
        data = f.read()

    # print(data)

    create_database()
    insert_to_database(data)
    # insert_to_database(data)
