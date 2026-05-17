import logging
import os
import requests
from flask import Flask, request
from dotenv import load_dotenv
from openai import OpenAI

# ================================
# Logging
# ================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ================================
# Load environment variables
# ================================
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MY_TELEGRAM_ID = int(os.getenv("MY_TELEGRAM_ID", "0"))

# ================================
# SAFE CONFIG CHECK (NO CRASH IN CI)
# ================================
if not TELEGRAM_TOKEN:
    logger.warning("TELEGRAM_BOT_TOKEN not set")

if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY not set")

# ================================
# OpenAI client (lazy-safe)
# ================================
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# ================================
# Flask app
# ================================
app = Flask(__name__)

# ================================
# Chat history
# ================================
chat_history = {}

# ================================
# System prompt
# ================================
SYSTEM_PROMPT = """
Ти — ввічливий персональний асистент Тетяни.
Ти не рекрутер. Ти лише збираєш інформацію та передаєш Тетяні.
"""

# ================================
# Response cleaner
# ================================
def clean_response(chat_id: int, text: str) -> str:
    import re

    clean_text = text.strip()

    forbidden_greetings = [
        "hello", "hi", "good day", "привіт", "вітаю",
        "добрий день", "дякую за повідомлення"
    ]

    changed = True
    while changed:
        changed = False
        text_lower = clean_text.lower()

        for word in forbidden_greetings:
            if text_lower.startswith(word):
                parts = re.split(r'[,.!?;:\n]', clean_text, maxsplit=1)
                clean_text = parts[1].strip() if len(parts) > 1 else clean_text
                changed = True
                break

    return clean_text

# ================================
# Telegram sender
# ================================
def send_telegram_message(chat_id: int, text: str):
    if not TELEGRAM_TOKEN:
        logger.warning("Telegram token missing, skip sending message")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }

    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        logger.error(f"Telegram send error: {e}")

# ================================
# ChatGPT logic
# ================================
def get_messages(chat_id, user_message):
    if chat_id not in chat_history:
        chat_history[chat_id] = [{"role": "system", "content": SYSTEM_PROMPT}]

    chat_history[chat_id].append({"role": "user", "content": user_message})

    if len(chat_history[chat_id]) > 11:
        chat_history[chat_id] = [chat_history[chat_id][0]] + chat_history[chat_id][-10:]

    return chat_history[chat_id]


def ask_chatgpt(chat_id: int, user_text: str) -> str:
    try:
        if not client:
            return "❌ AI service not configured"

        messages = get_messages(chat_id, user_text)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        reply = response.choices[0].message.content.strip()

        chat_history[chat_id].append({"role": "assistant", "content": reply})

        return reply

    except Exception as e:
        logger.error(f"ChatGPT error: {e}", exc_info=True)
        return "❌ Error generating response"

# ================================
# Routes
# ================================
@app.route("/", methods=["GET"])
def index():
    return "OK", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)

    if not data or "message" not in data:
        return "OK", 200

    message = data["message"]

    chat_id = message["chat"]["id"]
    username = message.get("from", {}).get("username", "unknown")
    text = message.get("text")

    if not text:
        return "OK", 200

    # /start
    if text.strip() == "/start":
        reply = "Hi, I'm Tatiana's assistant."
        send_telegram_message(chat_id, reply)
        return "OK", 200

    # AI reply
    reply = ask_chatgpt(chat_id, text)
    reply = clean_response(chat_id, reply)

    send_telegram_message(chat_id, reply)

    # forward to admin
    if MY_TELEGRAM_ID and chat_id != MY_TELEGRAM_ID:
        forward = f"👤 @{username}\n📝 {text}"
        send_telegram_message(MY_TELEGRAM_ID, forward)

    return "OK", 200


# ================================
# Run server
# ================================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, threaded=True)
