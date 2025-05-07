import json
import os
from collections import namedtuple
from enum import Enum

import dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer

from book import find_books_series_id_is_none, find_series_cosine_similarity, new_series, Series, model, \
    update_book_series_id


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

class TitleExtracted:
    def __init__(self, title: str, sub_title: str, episode: str):
        self.title = title
        self.sub_title = sub_title
        self.episode = episode

    def __str__(self):
        if self.sub_title is not None:
            return f"{self.title} ~{self.sub_title}~"
        else:
            return self.title

def extract_title(client: OpenAI, book_title: int) -> TitleExtracted:
    response = client.responses.create(
        model="gpt-4.1-2025-04-14",
        input=[
            {"role": "user", "content": book_title},
        ],
        previous_response_id=os.getenv("OPENAI_PREVIOUS_RESPONSE_ID"),
    )
    output_json = json.loads(response.output_text, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
    return TitleExtracted(
        title=output_json.t,
        sub_title=getattr(output_json, "s", None),
        episode=getattr(output_json, "r", None)
    )

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

    books = find_books_series_id_is_none(limit=99)

    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    title_structs = list(map(lambda b: extract_title(client=openai_client, book_title=b.title), books))
    titles = list(map(lambda t: str(t), title_structs))

    embedding_model = SentenceTransformer('nlpai-lab/KoE5')
    embeddings = embedding_model.encode(titles).tolist()

    for i, embedding in enumerate(embeddings):
        book = books[i]
        title = titles[i]
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
        print(f"{book.title}({title}) = {book.series_id}")

main()