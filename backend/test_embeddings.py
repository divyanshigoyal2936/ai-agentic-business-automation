from sentence_transformers import SentenceTransformer
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
print("MODEL NAME:", model)
embedding = model.encode("This is a test sentence.")
print(embedding)
print(len(embedding))