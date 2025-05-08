import typing

from sentence_transformers import SentenceTransformer

from book.model import Book, Site, Series
from book.repository import find_books_series_id_is_none, find_book_origins, find_series_by_isbn, new_series, \
    update_book_series_id, find_series_cosine_similarity, update_series_isbn
from prompt import SeriesPrompt


def get_books_series_none(limit: int = 10) -> list[Book]:
    books = find_books_series_id_is_none(limit)
    book_map: typing.Dict[int, Book] = {}
    book_ids: typing.List[int] = []

    for book in books:
        book_map[book.id] = book
        book_ids.append(book.id)

    origin_data = find_book_origins(book_ids)
    for origin in origin_data:
        if origin.book_id in book_map:
            book_map[origin.book_id].add_origin_data(origin)

    return books

def retrieve_series_isbn_in_book(book: Book) -> str | None:
    nlgo_origin = book.origin_data[Site.NLGO]
    if nlgo_origin is not None:
        series_isbn_property = next((o for o in nlgo_origin if o.property_name == "set_isbn"), None)
        if series_isbn_property is not None:
            return series_isbn_property.value
        else:
            return None
    else:
        return None

def normalize_and_retrieve_series_id(series_prompt: SeriesPrompt, embedding_model: SentenceTransformer, book: Book) -> int | None:
    series_title = series_prompt.normalization(book.title)
    series_embedded = embedding_model.encode([series_title.title]).tolist()[0]

    series_isbn = retrieve_series_isbn_in_book(book)
    similar_series = find_series_cosine_similarity(series_embedded)
    if len(similar_series) > 0:
        top = similar_series[0]
        if top.score is not None and top.score >= 0.98:
            series = top.series
            if series.isbn is None and series_isbn is not None:
                update_series_isbn(series.id, series_isbn)
            return top.series.id
        else:
            series = Series(name = series_title.title, vec = series_embedded, isbn = series_isbn)
            return new_series(series)
    else:
        series = Series(name = series_title.title, vec = series_embedded, isbn = series_isbn)
        return new_series(series)

def set_book_series_id(
        series_prompt: SeriesPrompt,
        embedding_model: SentenceTransformer,
        books: typing.List[Book]):
    for book in books:
        series_isbn = retrieve_series_isbn_in_book(book)
        if series_isbn is not None:
            series = find_series_by_isbn(series_isbn)
            if series is not None:
                update_book_series_id(book.id, series.id)
            else:
                series_id = normalize_and_retrieve_series_id(series_prompt, embedding_model, book)
                update_book_series_id(book.id, series_id)
        else:
            series_id = normalize_and_retrieve_series_id(series_prompt, embedding_model, book)
            update_book_series_id(book.id, series_id)