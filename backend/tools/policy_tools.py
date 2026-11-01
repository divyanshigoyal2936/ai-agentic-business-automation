from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
with open("company_policies.txt", "r", encoding="utf-8") as file:
    content = file.read()

chunks = content.split("\n\n")
embeddings = model.encode(chunks)


def search_policies(question):
    question_embedding = model.encode(question)
    similarity_scores = util.cos_sim(question_embedding, embeddings)
    best_chunk_index = similarity_scores.argmax()
    return chunks[best_chunk_index]