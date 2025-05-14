import json
import logging
from collections import namedtuple

from openai import OpenAI
from openai.types.responses import EasyInputMessageParam, Response
from pydantic import BaseModel


class SeriesNormalization:
    def __init__(self, origin: str, title: str):
        self.origin = origin
        self.title = title

    def __str__(self):
        return self.title

class _SeriesNormalizeResponse(BaseModel):
    title: str

class SimilarityFormat:
    def __init__(self,
                 title: str,
                 publisher_id: int):
        self.t = title
        self.p = publisher_id

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, ensure_ascii=False)

class SeriesPrompt:
    def __init__(self, client: OpenAI,
                 normalization_prompt_id: str,
                 similarity_prompt_id: str,):
        self.client = client
        self.normalization_prompt_id = normalization_prompt_id
        self.similarity_prompt_id = similarity_prompt_id

    def normalization(self, title: str) -> SeriesNormalization:
        logging.debug(f"제목의 노이즈 제거를 요청 합니다.: {title}")
        response = self.client.responses.parse(
            model="gpt-4.1-2025-04-14",
            input=title,
            previous_response_id=self.normalization_prompt_id,
            text_format=_SeriesNormalizeResponse,
        )
        logging.debug(f"노이즈 제거 프롬프트 응답: {response}")
        return SeriesNormalization(
            origin = title,
            title = response.output_parsed.title,
        )

    def similarity(self, new_book: SimilarityFormat, exists_books: list[SimilarityFormat]) -> (bool, float):
        prompt = f"기존 상품 리스트:[{','.join([i.to_json() for i in exists_books])}]\n신간 정보:{new_book.to_json()}"

        logging.info(f"시리즈 유사도 검사를 요청 합니다. {prompt}")
        response = self._request_response_api(prompt, self.similarity_prompt_id) # TODO parse로 변경하자...
        logging.info(f"유사도 프롬프트 output: {response.output_text}")

        output_json = json.loads(response.output_text, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
        return output_json.m, output_json.s

    def _request_response_api(self, prompt: str, prompt_id: str) -> Response:
        response = self.client.responses.create(
            model="gpt-4.1-2025-04-14",
            input=[
                EasyInputMessageParam(role="user", content=prompt)
            ],
            previous_response_id=prompt_id,
        )
        return response


