import sqlite3


class FilmesPipeline:
    def __init__(self) -> None:
        self.con = sqlite3.connect("../database.db")
        self.cur = self.con.cursor()

    def create_database(self):
        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS data (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            titulo_dublado TEXT UNIQUE NOT NULL,
            titulo TEXT, 
            imdb real, 
            ano INTEGER,
            genero TEXT,
            tamanho real,
            duracao integer,
            qualidade real,
            dublado BOOLEAN,
            sinopse TEXT,
            link TEXT)"""
        )

    def process_item(self, item, spider):
        self.cur.execute(
            """INSERT OR IGNORE INTO data
            (titulo_dublado, titulo, imdb, ano, genero, tamanho, duracao, qualidade, dublado, sinopse, link) 
            VALUES (:titulo_dublado, :titulo_original, :imdb, :ano, :genero, :tamanho, :duracao, 
            :qualidade, :dublado, :sinopse, :link)""",
            item,
        )
        self.con.commit()

        return item
