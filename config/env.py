import os

from dotenv import load_dotenv
from enum import Enum

class Env(Enum):
    LOCAL = "local"
    DEV = "dev"
    STAGING = "stg"
    PROD = "prod"

class DB:
    def __init__(self, host, port, username, password, schema):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.schema = schema

def load_db_config() -> DB:
    return DB(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", 5432),
        username=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        schema=os.getenv("DB_SCHEMA"),
    )

class OpenAI:
    def __init__(self, api_key, previous_response_id):
        self.api_key = api_key
        self.previous_response_id = previous_response_id

def load_openai_config() -> OpenAI:
    return OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        previous_response_id=os.getenv("OPENAI_PREVIOUS_RESPONSE_ID")
    )

def get_env() -> Env:
    env = os.getenv("PYTHON_ENV", "local").lower()
    try:
        return Env(env)
    except ValueError:
        return Env.LOCAL
