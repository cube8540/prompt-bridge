from dotenv import load_dotenv

from config.env import get_env, OpenAI, DB, load_db_config, load_openai_config


class Config:
    def __init__(self, db: DB, openai: OpenAI):
        self.db = db
        self.openai = openai

def load_config() -> Config:
    e = get_env()
    env_file = f".env.{e.value}"

    load_dotenv(dotenv_path=".env")
    load_dotenv(dotenv_path=env_file)

    db = load_db_config()
    openai = load_openai_config()

    return Config(db, openai)