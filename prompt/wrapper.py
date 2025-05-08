import json
from collections import namedtuple

from openai import OpenAI
from openai.types.responses import EasyInputMessageParam

class SeriesNormalization:
    def __init__(self, title: str, sub_title: str, episode: str):
        self.title = title
        self.sub_title = sub_title
        self.episode = episode

    def __str__(self):
        string = f"{self.title}"
        if self.sub_title is not None:
            string += f" ~{self.sub_title}~"
        if self.episode is not None:
            string += f" {self.episode}"
        return string

class SeriesPrompt:
    def __init__(self, client: OpenAI,
                 normalization_prompt_id: str):
        self.client = client
        self.normalization_prompt_id = normalization_prompt_id

    def normalization(self, title: str) -> SeriesNormalization:
        response = self.client.responses.create(
            model="gpt-4.1-2025-04-14",
            input=[
                EasyInputMessageParam(role="user", content=title)
            ],
            previous_response_id=self.normalization_prompt_id,
        )
        output_json = json.loads(response.output_text, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
        return SeriesNormalization(
            title = output_json.t,
            sub_title = getattr(output_json, "s", None),
            episode = getattr(output_json, "e", None)
        )