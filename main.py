import getopt
import logging.config
import os
import sys
from enum import Enum

import dotenv
import yaml
from openai import OpenAI
from psycopg_pool import ConnectionPool
from sentence_transformers import SentenceTransformer
from sympy import false

import book
import prompt
from book import series_retrieve


class Env(Enum):
    LOCAL = "local"
    DEV = "dev"
    PROD = "prod"

class CommandArguments:
    def __init__(self, isbn: list[str], limit: int):
        self.isbn = isbn
        self.limit = limit

def _get_env() -> Env:
    e = os.getenv("PYTHON_ENV", "local").lower()
    try:
        return Env(e)
    except ValueError:
        return Env.LOCAL

env = _get_env()
dotenv.load_dotenv(f".env.{env.value}")

logging_file = f"logging.{env.value}.yaml"
if os.path.exists(logging_file):
    with open(logging_file, 'rt') as file:
        logging_config = yaml.load(file.read(), Loader=yaml.FullLoader)
        logging.config.dictConfig(logging_config)
else:
    logging.basicConfig(level=logging.INFO)
    logging.warning(f"logging file {logging_file} not found")

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
    normalization_prompt_id = os.getenv("OPENAI_NORMALIZATION_PROMPT_ID"),
    similarity_prompt_id = os.getenv("OPENAI_SIMILARLY_PROMPT_ID")
)

embedding_transformer = SentenceTransformer('nlpai-lab/KoE5')

def main():
    isbn: list[str] | None = None
    limit: int = 10

    try:
        opts, etc_args = getopt.getopt(sys.argv[1:], "i:l", ["isbn=", "limit="]);
    except getopt.GetoptError:
        logging.error("main.py -i <isbn> -l <limit>")
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-i", "--isbn"):
            isbn = arg.split(",")
        elif opt in ("-l", "--limit"):
            limit = int(arg)
        else:
            logging.error("main.py -i <isbn> -l <limit>")
            sys.exit(2)

    try:
        db_connection_pool.open()
        book_repository = book.BookRepository(db_connection_pool)
        series_repository = book.SeriesRepository(db_connection_pool)

        standard_score = float(os.getenv("SIMILARITY_STANDARD_SCORE", 0.98))
        second_score = float(os.getenv("SIMILARITY_SECOND_SCORE", 0.7))

        main_title_series_retrieve = series_retrieve.MainTitleSeriesRetrieve(series_repository)
        main_title_series_retrieve.set_matched_score(standard_score)
        main_title_series_retrieve_wrapper = series_retrieve.SimilarPromptSeriesRetrieve(
            strategy=main_title_series_retrieve,
            prompt=series_prompt,
            book_repository=book_repository,
        )
        main_title_series_retrieve_wrapper.set_predicate(lambda m, series, s : standard_score > s >= second_score)

        retrieve_chain = series_retrieve.SeriesRetrieveChain()
        retrieve_chain.add_retrieve(main_title_series_retrieve_wrapper)

        script = book.BookAutoSeriesScript(
            book_repository = book_repository,
            series_repository = series_repository,
            series_prompt = series_prompt,
            series_retrieve_strategy = retrieve_chain,
            transformer = embedding_transformer
        )
        script.run(isbn = isbn, limit = limit)
    finally:
        db_connection_pool.close()

main()