import enum

import psycopg_pool
from psycopg.rows import dict_row


class PromptCode(enum.Enum):
    TITLE_NORMALIZE = "TITLE_NORMALIZE"
    SERIES_SIMILARITY = "SERIES_SIMILARITY"

class Prompt:
    code: PromptCode
    last_dialogue_id: str
    description: str

    def __init__(self, code: PromptCode, last_dialogue_id: str):
        self.code = code
        self.last_dialogue_id = last_dialogue_id

    def set_description(self, description: str):
        self.description = description

    def __str__(self):
        return f"code: {self.code}, last_dialogue_id: {self.last_dialogue_id}, description: {self.description}"


class PromptRepository:

    _SQL_FIND_PROMPT_BY_CODE = """SELECT code, last_dialogue_id, description FROM prompt.prompts WHERE code = %(code)s"""

    def __init__(self, pool: psycopg_pool.ConnectionPool):
        self._pool = pool

    def find_prompt(self, kind: PromptCode) -> Prompt:
        with self._pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(self._SQL_FIND_PROMPT_BY_CODE, {"code" : kind.value})
                row = cur.fetchone()
                prompt = Prompt(
                    code=PromptCode(row["code"].upper()),
                    last_dialogue_id=row["last_dialogue_id"],
                )
                prompt.set_description(row["description"])
                return prompt