import dataclasses
import json
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

class _NormalizeResponse(BaseModel):
    title: str
    reason: str | None

@dataclasses.dataclass
class NormalizeSaleInfo:
    site: str
    title: str
    price: int | None = None
    desc: str | None = None
    series: list[str] | None = None

    def __init__(self, **kwargs):
        names = set([f.name for f in dataclasses.fields(self)])
        for k, v in kwargs.items():
            if k in names:
                setattr(self, k, v)

    def to_dict(self):
        result: dict = {
            "site": self.site,
            "title": self.title,
        }
        if self.price is not None:
            result["price"] = self.price
        if self.desc is not None:
            result["desc"] = self.desc
        if self.series is not None:
            result["series"] = self.series
        return result

@dataclasses.dataclass
class NormalizeRequest:
    title: str
    sale_info: list[NormalizeSaleInfo] | None = None

    def __init__(self, **kwargs):
        names = set([f.name for f in dataclasses.fields(self)])
        for k, v in kwargs.items():
            if k in names:
                if k == "sale_info":
                    v = [NormalizeSaleInfo(**info) for info in v]
                setattr(self, k, v)

    def to_dict(self):
        result: dict = {"title": self.title}
        if self.sale_info is not None:
            result["sale_info"] = [info.to_dict() for info in self.sale_info]
        return result

    def to_json(self):
        return json.dumps(self.to_dict(), separators=(',', ':'), ensure_ascii=False)


class Bridge:
    def __init__(self, openai: OpenAI, repository: schema.PromptRepository):
        self._openai = openai
        self._repository = repository

    def normalize(self, req: NormalizeRequest) -> Normalization:
        prompt = self._repository.find_prompt(schema.PromptCode.TITLE_NORMALIZE)

        _input = req.to_json()
        logging.info(f"제목의 노이즈 제거를 요청 합니다: {_input} (previous_response_id: {prompt.last_dialogue_id})")
        response = self._openai.responses.parse(
            model=prompt.model,
            previous_response_id=prompt.last_dialogue_id,
            text_format=_NormalizeResponse,
            input=_input,
        )
        formated_response: _NormalizeResponse = response.output_parsed
        normalization = Normalization(
            original = req.title,
            title = formated_response.title,
            reason = formated_response.reason,
        )
        logging.info(f"노이즈 제거가 완료 되었습니다 (use: {prompt.last_dialogue_id}): {req.title} ===> {normalization}")
        logging.log(logging.NOTSET, f"{req.title} => {formated_response.reason}")
        return normalization