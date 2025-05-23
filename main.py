import atexit
import dataclasses
import logging
import os

from flask import Flask, request, jsonify
from openai import OpenAI
from sentence_transformers import SentenceTransformer

import cfg
import prompt

runtime_env = cfg.get_runtime_env()
cfg.set_global_logging_config(runtime_env)

db_connection_pool = cfg.connect_to_db_pool()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

prompt_repository = prompt.PromptRepository(db_connection_pool)
series_prompt = prompt.series.Bridge(openai_client, prompt_repository)

logging.info("nlpai-lab/KoE5 model loading...")
transformer = SentenceTransformer('nlpai-lab/KoE5')
logging.info("nlpai-lab/KoE5 model loading completed")
app = Flask(__name__)

@dataclasses.dataclass
class _TitleNormalizeRequest:
    title: str
    isbn: str           # 임시 추가
    desc: str | None    # 임시 추가
    price: int | None   # 임시 추가

@dataclasses.dataclass
class _TitleNormalizeResponse:
    title: str

@app.post("/normalize")
def normalize():
    body = request.get_json()
    _request = _TitleNormalizeRequest(**body)

    normalization = series_prompt.normalize(_request.title)
    _response = _TitleNormalizeResponse(title = normalization.title)

    return jsonify(_response)

@dataclasses.dataclass
class _EmbeddingRequest:
    text: list[str]

@dataclasses.dataclass
class _Embedding:
    original: str
    encode: list[float]

@dataclasses.dataclass
class _EmbeddingResponse:
    embeddings: list[_Embedding]

@app.post("/embedding")
def embedding():
    body = request.get_json()
    _request = _EmbeddingRequest(**body)

    encodes = transformer.encode(_request.text).tolist()
    embeddings: list[_Embedding] = []

    for idx, encode in enumerate(encodes):
        embeddings.append(_Embedding(original=_request.text[idx], encode=encode))

    _response = _EmbeddingResponse(embeddings=list(embeddings))
    return jsonify(_response)

db_connection_pool.open()

def cleanup():
    db_connection_pool.close()

atexit.register(cleanup)