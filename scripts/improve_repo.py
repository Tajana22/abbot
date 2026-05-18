import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# Read repository files
readme = read_file("README.md")

try:
    bot_code = read_file("main.py")
except FileNotFoundError:
    bot_code = ""


prompt = f"""
You are a senior DevOps and Software Engineer.

Improve this repository documentation safely.

Rules:
- Preserve existing functionality
- Do not invent fake features
- Improve:
  - README clarity
  - structure
  - formatting
  - developer documentation
  - setup instructions
  - DevOps quality
  - code comments suggestions

Return ONLY valid markdown for README.md.
Do not include explanations.
Do not use markdown code fences.

README:
{readme}

Application code:
{bot_code[:4000]}
"""

try:
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "You safely improve software repositories."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=2000
    )

    result = response.choices[0].message.content.strip()

    if result:
        write_file("README.md", result)
        print("README improved successfully")
    else:
        print("Empty response from model")

except Exception as e:
    print(f"AI improvement failed: {e}")
