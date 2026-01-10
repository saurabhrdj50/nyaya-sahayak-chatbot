import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

print("Checking available Groq models...")

try:
    models = client.models.list()
    for model in models.data:
        print("-", model.id)
except Exception as e:
    print("Error connecting to Groq:", e)
