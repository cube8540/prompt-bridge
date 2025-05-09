import os
from enum import Enum

import dotenv
from openai import OpenAI
from psycopg_pool import ConnectionPool
from sentence_transformers import SentenceTransformer
from sympy import false

import book
import prompt


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

dotenv.load_dotenv(f".env.{_get_env().value}")

db_connection_info: str = f"host={os.getenv('DB_HOST')} port={os.getenv('DB_PORT')} dbname={os.getenv('DB_NAME')} user={os.getenv('DB_USERNAME')} password={os.getenv('DB_PASSWORD')}"
db_connection_pool = ConnectionPool(
    conninfo=db_connection_info,
    open=false,
    max_idle=os.getenv("DB_MAX_IDLE", 10),
    min_size=os.getenv("DB_MIN_SIZE", 1),
    max_size=os.getenv("DB_MAX_SIZE", 10),
    max_waiting=os.getenv("DB_MAX_WAITING", 10),
    max_lifetime=os.getenv("DB_MAX_LIFETIME", 300),
)
db_connection_pool.autocommit = false

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
series_prompt = prompt.SeriesPrompt(
    client = openai_client,
    normalization_prompt_id = os.getenv("OPENAI_NORMALIZATION_PROMPT_ID")
)

embedding_transformer = SentenceTransformer('nlpai-lab/KoE5')

def main():
    try:
        db_connection_pool.open()
        book_repository = book.BookRepository(db_connection_pool)
        series_repository = book.SeriesRepository(db_connection_pool)
        script = book.BookAutoSeriesScript(
            book_repository = book_repository,
            series_repository = series_repository,
            series_prompt = series_prompt,
            transformer = embedding_transformer
        )
        script.run()
    finally:
        db_connection_pool.close()

main()