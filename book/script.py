import logging

from sentence_transformers import SentenceTransformer

from book.db import BookRepository, SeriesRepository
from book.model import Book, Series
from book.series_retrieve import SeriesRetrieveStrategy
from prompt import SeriesPrompt


class BookAutoSeriesScript:
    _series_match_score: float = 0.98

    def __init__(self,
                 book_repository: BookRepository,
                 series_repository: SeriesRepository,
                 series_prompt: SeriesPrompt,
                 series_retrieve_strategy: SeriesRetrieveStrategy,
                 transformer: SentenceTransformer):
        self._book_repository = book_repository
        self._series_repository = series_repository
        self._series_prompt = series_prompt
        self._series_retrieve_strategy = series_retrieve_strategy
        self._transformer = transformer

    def run(self,
            isbn: list[str] | None = None,
            limit: int = 10):
        books = self._retrieve_books(isbn=isbn, limit=limit)
        for book in books:
            series_isbn = book.retrieve_series_isbn()
            if series_isbn is not None:
                series_list = self._series_repository.find_by_isbn([series_isbn])
                if series_list is not None and len(series_list) == 1:
                    series = series_list[0]
                    self._book_repository.update_series_id(book.id, series.id)
                    continue

            series_id = self._normalize_and_retrieve_series_id(book)
            self._book_repository.update_series_id(book.id, series_id)

    def set_series_match_score(self, score: float):
        self._series_match_score = score

    def _retrieve_books(self,
                        isbn: list[str] | None = None,
                        limit: int = 10) -> list[Book] | None:
        if isbn is not None:
            books = self._book_repository.find_book_by_isbn(isbn)
        else:
            books = self._book_repository.find_series_id_none(limit)
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
        logging.info(f"제목 노이즈 제거 완료: {book} -> {normalize}")

        main_title_embedded = self._transformer.encode([normalize.title]).tolist()[0]
        series_isbn = book.retrieve_series_isbn()

        (matched, find_series, score) = self._series_retrieve_strategy.retrieve(book, main_title_embedded)
        if matched:
            if find_series.isbn is None and series_isbn is not None:
                self._series_repository.update_series_isbn(find_series.id, series_isbn)
            return find_series.id

        new_series = Series(name=normalize.title, isbn=series_isbn, main_title_vec=main_title_embedded)
        return self._series_repository.insert(new_series)