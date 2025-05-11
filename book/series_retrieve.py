from typing import Callable

from book.db import repository
from book.model import model
from prompt import SeriesPrompt
from prompt.wrapper import SimilarityFormat


class SeriesRetrieveStrategy:
    def retrieve(self, book: model.Book, main_title_vec: list[float]) -> (bool, model.Series | None, int):
        """
        도서 정보와 제목의 임베딩을 받아 데이터베이스에서 가장 유사한 시리즈를 찾아 반환합니다.

        :param book: 도서 정보
        :param main_title_vec: 책 제목 임베딩

        :return: (bool, Series, int) 지정된 기준 스코어 이상 인지 여부, 요청값과 가장 유사한 시리즈, 스코어
        """
        pass

class MainTitleSeriesRetrieve(SeriesRetrieveStrategy):
    _matched_score: float = 0.98

    def __init__(self, series_repository: repository.SeriesRepository):
        self._series_repository = series_repository

    def set_matched_score(self, score: float):
        self._matched_score = score

    def retrieve(self, book: model.Book, main_title_vec: list[float]) -> (bool, model.Series | None, int):
        similar = self._series_repository.cosine_similarity(main_title_vec)
        if len(similar) > 0:
            (top, score) = (similar[0])
            if score >= self._matched_score:
                return True, top, score
            else:
                return False, top, score

        return False, None, 0

class SimilarPromptSeriesRetrieve(SeriesRetrieveStrategy):

    _predicate: Callable[[bool, model.Series | None, int], bool] | None = None

    def __init__(self, strategy: SeriesRetrieveStrategy, prompt: SeriesPrompt, book_repository: repository.BookRepository):
        self._strategy = strategy
        self._prompt = prompt
        self._book_repository = book_repository

    def set_predicate(self, predicate: Callable[[bool, model.Series | None, int], bool]):
        self._predicate = predicate

    def retrieve(self, book: model.Book, main_title_vec: list[float]) -> (bool, model.Series | None, int):
        (matched, series, score) = self._strategy.retrieve(book, main_title_vec)
        if self._predicate is None or self._predicate(matched, series, score):
            series_books = list(map(lambda x : SimilarityFormat(title=x.title, publisher_id=x.publisher_id), self._book_repository.find_book_by_series_id(series.id)))[:5]
            new_book = SimilarityFormat(title=book.title, publisher_id=book.publisher_id)
            (new_matched, new_score) = self._prompt.similarity(new_book, series_books)
            if new_matched:
                return True, series, new_score

        return matched, series, score


class SeriesRetrieveChain(SeriesRetrieveStrategy):
    _retrieves: list[SeriesRetrieveStrategy] = []

    def add_retrieve(self, retrieve: SeriesRetrieveStrategy):
        self._retrieves.append(retrieve)

    def retrieve(self, book: model.Book, main_title_vec: list[float]) -> (bool, model.Series | None, int):
        for retrieve in self._retrieves:
            (matched, series, score) = retrieve.retrieve(book, main_title_vec)
            if matched:
                return matched, series, score
        return False, None, 0