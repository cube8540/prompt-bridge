from typing import List

import psycopg
from psycopg.rows import dict_row

import config
from book import Book


def connect(db_conf: config.DB):
    return psycopg.connect(
        dbname=db_conf.schema,
        user=db_conf.username,
        password=db_conf.password,
        host=db_conf.host,
        port=db_conf.port
    )

SQL_BOOK_SERIES_ID_NONE = """
    select id,
           isbn,
           title,
           publisher_id,
           scheduled_pub_date,
           actual_pub_date,
           series_id,
           registered_at,
           modified_at
    from books.book
    where series_id is null
    order by id desc
    limit %s
"""

class BookRepository:
    def __init__(self, db_conf: config.DB):
        self.db_conf = db_conf

    def find_series_id_none(self, limit: int = 10):
        connection = connect(self.db_conf)
        try:
            cursor = connection.cursor(row_factory=dict_row)
            cursor.execute(SQL_BOOK_SERIES_ID_NONE, (limit,))
            raw_books = cursor.fetchall()

            books = []
            for raw_book in raw_books:
                books.append(Book(
                    book_id = raw_book['id'],
                    isbn = raw_book['isbn'],
                    title = raw_book['title'],
                    publisher_id = raw_book['publisher_id'],
                    scheduled_pub_date = raw_book['scheduled_pub_date'],
                    actual_pub_date = raw_book['actual_pub_date'],
                    series_id = raw_book['series_id'],
                    registered_at = raw_book['registered_at'],
                    modified_at = raw_book['modified_at'],
                ))
            return books
        finally:
            connection.close()
