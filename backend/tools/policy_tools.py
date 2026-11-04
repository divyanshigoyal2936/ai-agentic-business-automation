import numpy as np
from fastembed import TextEmbedding

model = TextEmbedding("BAAI/bge-small-en-v1.5")

with open("company_policies.txt", "r", encoding="utf-8") as file:
    content = file.read()

chunks = [c for c in content.split("\n\n") if c.strip()]
embeddings = np.array(list(model.embed(chunks)))


def search_policies(question):
    question_embedding = next(iter(model.embed([question])))
    scores = embeddings @ question_embedding / (
        np.linalg.norm(embeddings, axis=1) * np.linalg.norm(question_embedding)
    )
    return chunks[int(scores.argmax())]