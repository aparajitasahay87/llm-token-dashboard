from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="http://localhost:8000/proxy/openai"
)

print("Sending test call through proxy...")

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "Say hello in one word"}
    ],
    max_tokens=10
)

print(f"Response: {response.choices[0].message.content}")
print(f"Tokens:   {response.usage.total_tokens}")
print(f"Model:    {response.model}")
print("Check proxy terminal for log entry.")
print("Check Supabase for new row.")
