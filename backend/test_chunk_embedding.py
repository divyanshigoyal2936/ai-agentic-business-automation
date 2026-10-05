from sentence_transformers import SentenceTransformer
from sentence_transformers import util


with open('company_policies.txt', 'r', encoding='utf-8') as file:
    content = file.read()
chunks = content.split('\n\n')  # Split the content into chunks based on double newlines    
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
embeddings = model.encode(chunks)
print("CHUNKS REPR:", repr(chunks[1]))
print(len(embeddings))
print(len(embeddings[0]))  # Print the length of the first embedding vector
print

question ="Agar mujhe product pasand nahi aaya toh paisa wapas kaise milega?"
print("QUESTION REPR:", repr(question)) 
question_embedding = model.encode(question)
similarities = util.cos_sim(question_embedding, embeddings)
print(similarities)
best_match_index = similarities.argmax()
print(f"Best matching policy chunk index: {best_match_index}")
print(chunks[best_match_index])  # Print the best matching policy chunk