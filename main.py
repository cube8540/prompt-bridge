import os
from enum import Enum

import dotenv
from sentence_transformers import SentenceTransformer

from book import find_books_series_id_is_none, find_series_cosine_similarity, new_series, Series, Book


class Env(Enum):
    LOCAL = "local"
    DEV = "dev"
    PROD = "prod"

def _get_env() -> Env:
    env = os.getenv("PYTHON_ENV", "local").lower()
    try:
        return Env(env)
    except ValueError:
        return Env.LOCAL

def main():
    env = _get_env()
    dotenv.load_dotenv(f".env.{env.value}")

    books = find_books_series_id_is_none()
    titles = list(map(lambda b: b.title, books)) # 이 부분을 타이틀 -> OpenAI 사용

    model = SentenceTransformer('nlpai-lab/KoE5')
    embeddings = model.encode(titles).tolist()

    groups = []
    for i, embedding in enumerate(embeddings):
        book = books[i]
        similar_series = find_series_cosine_similarity(embedding)
        top = similar_series[0]
        if len(similar_series) == 0 or top.score is None or top.score < 0.90:
            series = Series(series_id = 0, name=book.title, vec=embedding)
            series_id = new_series(series)
            book.series_id = series_id
        else:
            book.series_id = top.series.id

        print(f"{book.title} = {book.series_id}")

main()