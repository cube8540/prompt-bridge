from sentence_transformers import SentenceTransformer

from book.db import BookRepository, SeriesRepository
from book.model import Book, Series
from prompt import SeriesPrompt


class BookAutoSeriesScript:
    def __init__(self,
               book_repository: BookRepository,
               series_repository: SeriesRepository,
               series_prompt: SeriesPrompt,
               transformer: SentenceTransformer):
        self._book_repository = book_repository
        self._series_repository = series_repository
        self._series_prompt = series_prompt
        self._transformer = transformer

    def run(self, limit: int = 10):
        books = self._retrieve_books_series_none(limit)
        for book in books:
            series_isbn = book.retrieve_series_isbn()
            if series_isbn is not None:
                series_list = self._series_repository.find_by_isbn([series_isbn])
                if series_list is not None and len(series_list) == 1:
                    series = series_list[0]
                    self._book_repository.update_series_id(book.id, series.id)
                else:
                    series_id = self._normalize_and_retrieve_series_id(book)
                    self._book_repository.update_series_id(book.id, series_id)
            else:
                series_id = self._normalize_and_retrieve_series_id(book)
                self._book_repository.update_series_id(book.id, series_id)

    def _retrieve_books_series_none(self, limit: int = 10) -> list[Book] | None:
        books = self._book_repository.find_series_id_none(limit = limit)
        book_map = {}
        book_ids = []

        for book in books:
            book_map[book.id] = book
            book_ids.append(book.id)

        origins = self._book_repository.find_book_origins(book_ids)
        for origin in origins:
            if origin.book_id in book_map:
                book_map[origin.book_id].add_origin_data(origin)

        return books

    def _normalize_and_retrieve_series_id(self, book: Book) -> int | None:
        normalize = self._series_prompt.normalization(book.title)
        series_title_embedded = self._transformer.encode([normalize.title]).tolist()[0]

        series_isbn = book.retrieve_series_isbn()
        similar_series = self._series_repository.cosine_similarity(series_title_embedded)
        if len(similar_series) > 0 :
            (top, score) = (similar_series[0])
            if score >= 0.98:
                if top.isbn is None and series_isbn is not None:
                    self._series_repository.update_series_isbn(top.id, series_isbn)
                return top.id
            else:
                series = Series(name = normalize.title, vec = series_title_embedded, isbn = series_isbn)
                return self._series_repository.insert(series)
        else:
            series = Series(name = normalize.title, vec = series_title_embedded, isbn = series_isbn)
            return self._series_repository.insert(series)