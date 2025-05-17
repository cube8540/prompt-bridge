import enum
import logging.config
import os

import dotenv
import yaml
from psycopg_pool import ConnectionPool


class RuntimeEnv(enum.Enum):
    LOCAL = "local"
    DEV = "dev"
    PROD = "prod"

def get_runtime_env() -> RuntimeEnv:
    e = os.getenv("PYTHON_ENV", "local").lower()
    dotenv.load_dotenv(f".env.{e}")
    try:
        return RuntimeEnv(e)
    except ValueError:
        return RuntimeEnv.LOCAL

def set_global_logging_config(runtime: RuntimeEnv):
    logging_file = f"logging.{runtime.value}.yaml"
    if os.path.exists(logging_file):
        with open(logging_file, 'rt') as file:
            logging_config = yaml.load(file.read(), Loader=yaml.FullLoader)
            logging.config.dictConfig(logging_config)
    else:
        logging.basicConfig(level=logging.INFO)
        logging.warning(f"logging file {logging_file} not found")

def connect_to_db_pool() -> ConnectionPool:
    db_connection_info: str = f"host={os.getenv('DB_HOST')} port={os.getenv('DB_PORT')} dbname={os.getenv('DB_NAME')} user={os.getenv('DB_USERNAME')} password={os.getenv('DB_PASSWORD')}"
    db_connection_pool = ConnectionPool(
        conninfo=db_connection_info,
        open=False,
        max_idle=os.getenv("DB_MAX_IDLE", 10),
        min_size=os.getenv("DB_MIN_SIZE", 1),
        max_size=os.getenv("DB_MAX_SIZE", 10),
        max_waiting=os.getenv("DB_MAX_WAITING", 10),
        max_lifetime=os.getenv("DB_MAX_LIFETIME", 300),
    )
    db_connection_pool.autocommit = False
    return db_connection_pool