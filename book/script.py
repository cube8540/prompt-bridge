import logging

from sentence_transformers import SentenceTransformer

from book.db import BookRepository, SeriesRepository
from book.model import Book, Series
from prompt import SeriesPrompt


class BookAutoSeriesScript:
    _series_match_score: float = 0.98

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
                    continue

            series_id = self._normalize_and_retrieve_series_id(book)
            self._book_repository.update_series_id(book.id, series_id)

    def set_series_match_score(self, score: float):
        self._series_match_score = score

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
        logging.info(f"제목 노이즈 제거 완료: {book} -> {normalize}")

        series_title_embedded = self._transformer.encode([normalize.title]).tolist()[0]
        series_isbn = book.retrieve_series_isbn()

        similar_series = self._series_repository.cosine_similarity(series_title_embedded)
        if len(similar_series) > 0 :
            (top, score) = (similar_series[0])
            if score >= self._series_match_score:
                logging.info(f"이미 저장된 시리즈를 찾아 해당 시리즈 아이디를 반환합니다.: {book}/{normalize.title} -> {top} (스코어: {score})")
                if top.isbn is None and series_isbn is not None:
                    logging.info(f"시리즈의 ISBN을 업데이트 합니다.: {top} -> {series_isbn}")
                    self._series_repository.update_series_isbn(top.id, series_isbn)
                return top.id
            else:
                logging.info(f"{book}/{normalize.title} -> {top} 기준치({self._series_match_score}) 미달로 인한 시리즈 불일치 스코어: {score}")

        series = Series(name = normalize.title, vec = series_title_embedded, isbn = series_isbn)
        logging.debug(f"새로운 시리즈를 생성 합니다. {series}")
        return self._series_repository.insert(series)