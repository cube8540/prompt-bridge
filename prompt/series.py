import dataclasses
import logging

from openai import OpenAI
from pydantic import BaseModel

from prompt import schema


@dataclasses.dataclass
class Normalization:
    original: str
    title: str
    reason: str | None

    def __str__(self):
        return f"original: {self.original}, title: {self.title}, reason: {self.reason}"

class _NormalizationResponse(BaseModel):
    title: str
    reason: str | None

class Bridge:
    def __init__(self, openai: OpenAI, repository: schema.PromptRepository):
        self._openai = openai
        self._repository = repository

    def normalize(self, title: str) -> Normalization:
        prompt = self._repository.find_prompt(schema.PromptCode.TITLE_NORMALIZE)

        logging.info(f"제목의 노이즈 제거를 요청 합니다: {title} (previous_response_id: {prompt.last_dialogue_id})")
        response = self._openai.responses.parse(
            model=prompt.model,
            previous_response_id=prompt.last_dialogue_id,
            text_format=_NormalizationResponse,
            input=title,
        )
        formated_response: _NormalizationResponse = response.output_parsed
        normalization = Normalization(
            original = title,
            title = formated_response.title,
            reason = formated_response.reason,
        )
        logging.info(f"노이즈 제거가 완료 되었습니다 (use: {prompt.last_dialogue_id}): {title} ===> {normalization}")
        logging.log(logging.NOTSET, f"{title} => {formated_response.reason}")
        return normalization