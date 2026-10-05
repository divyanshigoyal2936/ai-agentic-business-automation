import os 
from dotenv import load_dotenv
from groq import Groq

load_dotenv()   

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)
response = client.chat.completions.create(
    model="openai/gpt-oss-120b",  
    max_tokens=100,
    messages=[
        {"role": "user", "content": "Who are you?"},
    ]   
)
print(response.choices[0].message.content)