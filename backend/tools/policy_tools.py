from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
print("ACTUAL MODEL PATH:", model[0].auto_model.config._name_or_path)
with open("company_policies.txt", "r", encoding="utf-8") as file:
    content = file.read()

chunks = content.split("\n\n")
embeddings = model.encode(chunks)
print("CHUNKS REPR:", repr(chunks[1]))


def search_policies(question):
    print("QUESTION REPR:", repr(question))    
    question_embedding = model.encode(question)
    print("QUESTION EMBEDDING SAMPLE:", question_embedding[:5])
    print("REFUND CHUNK EMBEDDING SAMPLE:", embeddings[1][:5])
    similarity_scores = util.cos_sim(question_embedding, embeddings)
    print("Scores:", similarity_scores)
    best_chunk_index = similarity_scores.argmax()
    print("Best index:", best_chunk_index)
    return chunks[best_chunk_index]