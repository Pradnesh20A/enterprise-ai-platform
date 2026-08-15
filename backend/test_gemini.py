import os
from dotenv import load_dotenv
from google import genai

load_dotenv("../.env")
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
for m in client.models.list():
    print(m.name)
