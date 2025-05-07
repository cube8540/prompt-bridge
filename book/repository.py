from psycopg.rows import dict_row

import db
from book import model

_SQL_BOOK_SERIES_ID_NONE = """
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
    limit %(limit)s
"""

_SQL_SERIES_COSINE_SIMILARITY = """
    select id,
           name,
           isbn,
           vec,
           1 - (vec <=>  %(vector)s) as score,
           registered_at,
           modified_at
    from books.series
    order by vec <=> %(vector)s
    limit 5
"""

_SQL_SERIES_INSERT = """
    insert into books.series (name, isbn, vec)
    values (%(name)s, %(isbn)s, %(vec)s)
    returning id
 """

_SQL_BOOK_UPDATE_SERIES_ID = """
    update books.book
    set series_id = %(series_id)s
    where id = %(book_id)s
"""


def find_books_series_id_is_none(limit: int = 10) -> list[model.Book] | None:
    connection = db.connection()
    try:
        cursor = connection.cursor(row_factory=dict_row)
        cursor.execute(_SQL_BOOK_SERIES_ID_NONE, {"limit": limit,})

        return list(map(_row_to_book, cursor.fetchall()))
    finally:
        connection.close()

def update_book_series_id(book_id: int, series_id: int) -> int | None:
    connection = db.connection()
    try:
        cursor = connection.cursor()
        cursor.execute(_SQL_BOOK_UPDATE_SERIES_ID, {"series_id": series_id, "book_id": book_id})
        row_count = cursor.rowcount
        connection.commit()
        return row_count
    finally:
        connection.close()

class SeriesWithScore:
    def __init__(self, series: model.Series, score: float):
        self.series = series
        self.score = score

def find_series_cosine_similarity(vector: list[float]) -> list[SeriesWithScore] | None:
    connection = db.connection()
    try:
        cursor = connection.cursor(row_factory=dict_row)
        cursor.execute(_SQL_SERIES_COSINE_SIMILARITY, {"vector": str(vector),})

        series = []
        for row in cursor.fetchall():
            s = _row_to_series(row)
            score = row['score']
            series.append(SeriesWithScore(s, score))
        return series
    finally:
        connection.close()

def new_series(series: model.Series) -> int | None:
    connection = db.connection()
    try:
        cursor = connection.cursor()
        cursor.execute(_SQL_SERIES_INSERT, { "name": series.name, "isbn": series.isbn, "vec": series.vec })
        connection.commit()

        series_id = cursor.fetchone()[0]
        return series_id
    finally:
        connection.close()

def _row_to_book(row) -> model.Book:
    return model.Book(
        book_id = row['id'],
        isbn = row['isbn'],
        title = row['title'],
        publisher_id = row['publisher_id'],
        scheduled_pub_date = row['scheduled_pub_date'],
        actual_pub_date = row['actual_pub_date'],
        series_id = row['series_id'],
        registered_at = row['registered_at'],
    )

def _row_to_series(row) -> model.Series:
    return model.Series(
        series_id = row['id'],
        name = row['name'],
        isbn= row['isbn'],
        registered_at = row['registered_at'],
        modified_at = row['modified_at'],
        vec= row['vec']
    )