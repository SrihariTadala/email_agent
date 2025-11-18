from groq import Groq
import os
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()   # <-- this loads .env file

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

print("\n=== AVAILABLE MODELS IN YOUR ACCOUNT ===")
models = client.models.list()

for m in models.data:
    print("-", m.id)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

print("\n=== AVAILABLE MODELS IN YOUR ACCOUNT ===")
models = client.models.list()

for m in models.data:
    print("-", m.id)
