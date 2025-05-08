import datetime

from psycopg.rows import dict_row

import db
from book.model import Book, BookOriginData, Series, Site

_SQL_BOOK_SERIES_ID_NONE = """
    select  id,
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

_SQL_BOOK_ORIGIN_DATA = """
    select  book_id,
            site,
            property,
            val
    from books.book_origin_data
    where book_id = ANY(%(book_id)s)
"""

_SQL_SERIES_COSINE_SIMILARITY = """
    select  id,
            name,
            isbn,
            vec,
            1 - (vec <=>  %(vector)s) as score,
            registered_at,
            modified_at
    from books.series
    order by vec <=> %(vector)s
    limit %(limit)s
"""

_SQL_SERIES_BY_ISBN = """
    select  id,
            name,
            isbn,
            vec,
            registered_at,
            modified_at
    from books.series
    where isbn = ANY(%(isbn)s)
"""

_SQL_SERIES_INSERT = """
    insert into books.series (name, isbn, vec, registered_at)
    values (%(name)s, %(isbn)s, %(vec)s, %(registered_at)s)
    returning id
 """

_SQL_SERIES_UPDATE_ISBN = """
    update books.series
    set isbn = %(isbn)s,
        modified_at = %(modified_at)s
    where id = %(series_id)s
"""

_SQL_BOOK_UPDATE_SERIES_ID = """
    update books.book
    set series_id = %(series_id)s,
        modified_at = %(modified_at)s
    where id = %(book_id)s
"""


def find_books_series_id_is_none(limit: int = 10) -> list[Book] | None:
    connection = db.connection()
    try:
        cursor = connection.cursor(row_factory=dict_row)
        cursor.execute(_SQL_BOOK_SERIES_ID_NONE, {"limit": limit,})

        return list(map(_row_to_book, cursor.fetchall()))
    finally:
        connection.close()

def find_book_origins(book_ids: list[int]) -> list[BookOriginData] | None:
    connection = db.connection()
    try:
        cursor = connection.cursor(row_factory=dict_row)
        cursor.execute(_SQL_BOOK_ORIGIN_DATA, {"book_id": book_ids,})

        return list(map(_row_to_book_origin_data, cursor.fetchall()))
    finally:
        connection.close()

def update_book_series_id(book_id: int, series_id: int) -> int | None:
    connection = db.connection()
    try:
        cursor = connection.cursor()
        cursor.execute(_SQL_BOOK_UPDATE_SERIES_ID, {"series_id": series_id, "book_id": book_id, "modified_at": datetime.datetime.now()})
        row_count = cursor.rowcount
        connection.commit()
        return row_count
    finally:
        connection.close()

class SeriesWithScore:
    def __init__(self, series: Series, score: float):
        self.series = series
        self.score = score

def find_series_by_isbn(isbn: str) -> Series | None:
    connection = db.connection()
    try:
        cursor = connection.cursor(row_factory=dict_row)
        cursor.execute(_SQL_SERIES_BY_ISBN, {"isbn": [isbn],})

        series = cursor.fetchone()
        if series is not None:
            return _row_to_series(series)
        else:
            return None
    finally:
        connection.close()

def find_series_by_isbns(isbn: list[str]) -> list[Series] | None:
    connection = db.connection()
    try:
        cursor = connection.cursor(row_factory=dict_row)
        cursor.execute(_SQL_SERIES_BY_ISBN, {"isbn": isbn,})
        return list(map(_row_to_series, cursor.fetchall()))
    finally:
        connection.close()

def find_series_cosine_similarity(vector: list[float], limit: int = 5) -> list[SeriesWithScore] | None:
    connection = db.connection()
    try:
        cursor = connection.cursor(row_factory=dict_row)
        cursor.execute(_SQL_SERIES_COSINE_SIMILARITY, {"vector": str(vector), "limit": limit,})

        series = []
        for row in cursor.fetchall():
            s = _row_to_series(row)
            score = row['score']
            series.append(SeriesWithScore(s, score))
        return series
    finally:
        connection.close()

def new_series(series: Series) -> int | None:
    connection = db.connection()
    try:
        cursor = connection.cursor()
        cursor.execute(_SQL_SERIES_INSERT, { "name": series.name, "isbn": series.isbn, "vec": series.vec, "registered_at": datetime.datetime.now() })
        connection.commit()

        series_id = cursor.fetchone()[0]
        return series_id
    finally:
        connection.close()

def update_series_isbn(series_id: int, isbn: str) -> int | None:
    connection = db.connection()
    try:
        cursor = connection.cursor()
        cursor.execute(_SQL_SERIES_UPDATE_ISBN, {"series_id": series_id, "isbn": isbn, "modified_at": datetime.datetime.now()})
        connection.commit()
        return cursor.rowcount
    finally:
        connection.close()

def _row_to_book(row) -> Book:
    return Book(
        book_id = row['id'],
        isbn = row['isbn'],
        title = row['title'],
        publisher_id = row['publisher_id'],
        scheduled_pub_date = row['scheduled_pub_date'],
        actual_pub_date = row['actual_pub_date'],
        series_id = row['series_id'],
        registered_at = row['registered_at'],
    )

def _row_to_series(row) -> Series:
    return Series(
        series_id = row['id'],
        name = row['name'],
        isbn= row['isbn'],
        registered_at = row['registered_at'],
        modified_at = row['modified_at'],
        vec= row['vec']
    )

def _row_to_book_origin_data(row) -> BookOriginData:
    return BookOriginData(
        book_id = row['book_id'],
        site = Site(row['site'].lower()),
        property_name = row['property'],
        value = row['val']
    )