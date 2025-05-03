import os
from openai import OpenAI

# This will look for OPENAI_API_KEY in your env by default
client = OpenAI()

print("OPENAI_API_KEY is set:", bool(os.getenv("OPENAI_API_KEY")))

try:
    resp = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user",   "content": "Hello!"}
        ],
        max_tokens=1,
        temperature=0
    )
    print("✅ Key is valid! API responded with:", resp.choices[0].message.content)
except Exception as e:
    print("❌ API call failed:", e)
