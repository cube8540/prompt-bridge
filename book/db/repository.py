import datetime

import psycopg_pool
from psycopg.rows import dict_row

from book.model import Book, BookOriginData, Series

class BookRepository:
    _SQL_SELECT_BOOK_SERIES_NONE: str = """
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

    _SQL_SELECT_BOOK_ORIGIN_DATA = """
        select book_id,
               site,
               property,
               val
        from books.book_origin_data
        where book_id = ANY (%(book_id)s)
    """

    _SQL_UPDATE_BOOK_SERIES_ID = """
        update books.book
        set series_id = %(series_id)s,
            modified_at = %(modified_at)s
        where id = %(book_id)s
    """

    def __init__(self, pool: psycopg_pool.ConnectionPool):
        self._pool = pool

    def find_series_id_none(self, limit: int = 10) -> list[Book] | None:
        with self._pool.connection() as _conn:
            with _conn.cursor(row_factory=dict_row) as _cur:
                _cur.execute(self._SQL_SELECT_BOOK_SERIES_NONE, {"limit": limit, })
                return list(map(_row_to_book, _cur.fetchall()))

    def find_book_origins(self, book_ids: list[int]) -> list[BookOriginData] | None:
        with self._pool.connection() as _conn:
            with _conn.cursor(row_factory=dict_row) as _cur:
                _cur.execute(self._SQL_SELECT_BOOK_ORIGIN_DATA, {"book_id": book_ids, })
                return list(map(_row_to_book_origin_data, _cur.fetchall()))

    def update_series_id(self, book_id: int, series_id: int) -> int | None:
        with self._pool.connection() as _conn:
            with _conn.cursor(row_factory=dict_row) as _cur:
                _cur.execute(self._SQL_UPDATE_BOOK_SERIES_ID, {"series_id": series_id, "book_id": book_id, "modified_at": datetime.datetime.now()})
                _conn.commit()
                return _cur.rowcount

class SeriesRepository:
    _SQL_SELECT_COSINE_SIMILARITY = """
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

    _SQL_SELECT_BY_ISBN = """
        select  id,
                name,
                isbn,
                vec,
                registered_at,
                modified_at
        from books.series
        where isbn = ANY(%(isbn)s)
    """

    _SQL_INSERT = """
        insert into books.series (name, isbn, vec, registered_at)
        values (%(name)s, %(isbn)s, %(vec)s, %(registered_at)s)
        returning id
    """

    _SQL_UPDATE_SERIES_ISBN = """
        update books.series
        set isbn = %(isbn)s,
            modified_at = %(modified_at)s
        where id = %(series_id)s
    """

    def __init__(self, pool: psycopg_pool.ConnectionPool):
        self._pool = pool

    def cosine_similarity(self, vector: list[float], limit: int = 5) -> list[tuple[Series, int]] | None:
        with self._pool.connection() as _conn:
            with _conn.cursor(row_factory=dict_row) as _cur:
                _cur.execute(self._SQL_SELECT_COSINE_SIMILARITY, {"vector": str(vector), "limit": limit,})
                return list(map(lambda row: (_row_to_series(row), row['score']), _cur.fetchall()))

    def find_by_isbn(self, isbn: list[str]) -> list[Series] | None:
        with self._pool.connection() as _conn:
            with _conn.cursor(row_factory=dict_row) as _cur:
                _cur.execute(self._SQL_SELECT_BY_ISBN, {"isbn": isbn,})
                return list(map(_row_to_series, _cur.fetchall()))

    def insert(self, series: Series) -> int | None:
        with self._pool.connection() as _conn:
            with _conn.cursor(row_factory=dict_row) as _cur:
                _cur.execute(self._SQL_INSERT, { "name": series.name, "isbn": series.isbn, "vec": series.vec, "registered_at": datetime.datetime.now() })
                _conn.commit()
                return _cur.fetchone()[0]

    def update_series_isbn(self, series_id: int, isbn: str) -> int | None:
        with self._pool.connection() as _conn:
            with _conn.cursor(row_factory=dict_row) as _cur:
                _cur.execute(self._SQL_UPDATE_SERIES_ISBN, {"series_id": series_id, "isbn": isbn, "modified_at": datetime.datetime.now()})
                _conn.commit()
                return _cur.rowcount


def _row_to_series(row) -> Series:
    return Series(
        series_id = row['id'],
        name = row['name'],
        isbn= row['isbn'],
        registered_at = row['registered_at'],
        modified_at = row['modified_at'],
        vec= row['vec']
    )

def _row_to_book(row) -> Book:
    return Book(
        book_id=row['id'],
        isbn=row['isbn'],
        title=row['title'],
        publisher_id=row['publisher_id'],
        scheduled_pub_date=row['scheduled_pub_date'],
        actual_pub_date=row['actual_pub_date'],
        series_id=row['series_id'],
        registered_at=row['registered_at'],
    )

def _row_to_book_origin_data(row) -> BookOriginData:
    return BookOriginData(
        book_id = row['book_id'],
        site = Site(row['site'].lower()),
        property_name = row['property'],
        value = row['val']
    )