import os
from enum import Enum

import dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer

import prompt
from book.script import get_books_series_none, set_book_series_id


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

    openapi_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    series_prompt = prompt.SeriesPrompt(
        client = openapi_client,
        normalization_prompt_id = os.getenv("OPENAI_NORMALIZATION_PROMPT_ID")
    )
    embedding_model = SentenceTransformer('nlpai-lab/KoE5')

    books = get_books_series_none(limit=10)
    set_book_series_id(series_prompt, embedding_model, books)

main()