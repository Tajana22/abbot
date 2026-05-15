import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# беремо README + код бота
readme = read_file("README.md")

try:
    bot_code = read_file("bot.py")
except:
    bot_code = ""

prompt = f"""
You are a senior DevOps/Software Engineer.

Your task:
Improve this Telegram bot repository.

Rules:
- DO NOT break bot functionality
- DO NOT invent new features
- Only improve:
  - README clarity
  - documentation
  - structure suggestions
  - code comments
  - best practices

Repository README:
{readme}

Bot code:
{bot_code}
"""

response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {"role": "system", "content": "You improve software projects safely."},
        {"role": "user", "content": prompt}
    ]
)

result = response.choices[0].message.content

write_file("README.md", result)

print("Repo improved successfully")
