import dataclasses
import logging

from openai import OpenAI
from pydantic import BaseModel

from prompt import schema


@dataclasses.dataclass
class Normalization:
    original: str
    title: str
    sub_title: str | None
    episode: str | None
    reason: str | None

    def __str__(self):
        if self.sub_title is not None:
            return f"{self.title} {self.sub_title}"
        else:
            return self.title

class _NormalizationResponse(BaseModel):
    title: str
    sub_title: str
    episode: str
    reason: str

class Bridge:
    def __init__(self, openai: OpenAI, repository: schema.PromptRepository):
        self._openai = openai
        self._repository = repository

    def normalize(self, title: str) -> Normalization:
        prompt = self._repository.find_prompt(schema.PromptCode.TITLE_NORMALIZE)

        logging.info(f"제목의 노이즈 제거를 요청 합니다: {title} (previous_response_id: {prompt.last_dialogue_id})")
        response = self._openai.responses.parse(
            model="gpt-4.1-2025-04-14",
            previous_response_id=prompt.last_dialogue_id,
            text_format=_NormalizationResponse,
            input=title,
        )
        formated_response: _NormalizationResponse = response.output_parsed
        normalization = Normalization(
            original = title,
            title = formated_response.title,
            sub_title = formated_response.sub_title,
            episode = formated_response.episode,
            reason = formated_response.reason,
        )
        logging.info(f"노이즈 제거가 완료 되었습니다 (use: {prompt.last_dialogue_id}): {title} ===> {normalization}")
        logging.log(logging.NOTSET, f"{title} => {formated_response.reason}")
        return normalization