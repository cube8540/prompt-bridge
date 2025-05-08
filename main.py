import os
from enum import Enum

import dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer

import prompt
from book import find_books_series_id_is_none, find_series_cosine_similarity, new_series, Series, update_book_series_id


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

def create_series(title: str, embedding: list[float]) -> int | None:
    new = Series(
        series_id = 0,
        name=title,
        vec=embedding
    )
    return new_series(new)

def main():
    env = _get_env()
    dotenv.load_dotenv(f".env.{env.value}")

    openapi_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    books = find_books_series_id_is_none(limit=10)
    series_prompt = prompt.SeriesPrompt(
        client = openapi_client,
        normalization_prompt_id = os.getenv("OPENAI_NORMALIZATION_PROMPT_ID")
    )

    normalizations = list(map(lambda b: series_prompt.normalization(b.title), books))
    for normalization in normalizations:
        print(f"normalized.title -> {normalization.title}")
        print(f"normalized.sub_title -> {normalization.sub_title}")
        print(f"normalized.episode -> {normalization.episode}")
        print("----------------------------------------------------------")

    series_titles = list(map(lambda n: n.title, normalizations))

    embedding_model = SentenceTransformer('nlpai-lab/KoE5')
    embeddings = embedding_model.encode(series_titles).tolist()

    for i, embedding in enumerate(embeddings):
        book = books[i]
        title = series_titles[i]
        similar_series = find_series_cosine_similarity(embedding)
        if len(similar_series) == 0:
            book.series_id = create_series(title, embedding)
        else:
            top = similar_series[0]
            if top.score is None or top.score < 0.98:
                book.series_id = create_series(title, embedding)
            else:
                book.series_id = top.series.id

        update_book_series_id(book.id, book.series_id)
        print(f"{book.title} -> ({title}) = {book.series_id}")
main()