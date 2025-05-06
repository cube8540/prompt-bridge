import json
from collections import namedtuple
from openai import OpenAI
from sentence_transformers import SentenceTransformer

import psycopg

from book.repo import BookRepository
from config import load_config

config = load_config()
book_repository = BookRepository(config.db)

books = book_repository.find_series_id_none(limit=10)

titles = []
for book in books:
    titles.append(book.title)

client = OpenAI(api_key=config.openai.api_key)

series_titles = []
for title in titles:
    response = client.responses.create(
        model="gpt-4.1-2025-04-14",
        input=[
            {"role": "user", "content": title},
        ],
        previous_response_id=config.openai.previous_response_id
    )

    output = json.loads(response.output_text, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
    series_titles.append(output.t)

model = SentenceTransformer('nlpai-lab/KoE5')
embeddings = model.encode(series_titles)

emb = []
for embedding in embeddings:
    emb.append(embedding.tolist())

for idx, e in enumerate(emb):
    title = series_titles[idx]
    print(title, e)
    cursor.execute("insert into books.series (name, vec) values (%s, %s)", (title, e))

connection.commit()
connection.close()
print("done")