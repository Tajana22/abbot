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

if not TELEGRAM_TOKEN:
    raise RuntimeError("❌ TELEGRAM_BOT_TOKEN not found")
if not OPENAI_API_KEY:
    raise RuntimeError("❌ OPENAI_API_KEY not found")

logger.info("Secrets loaded successfully")

# ================================
# OpenAI client
# ================================
client = OpenAI(api_key=OPENAI_API_KEY)

# ================================
# System prompt (Recruiter assistant)
# ================================
SYSTEM_PROMPT = """
Ти — лаконічний асистент Тетяни. Твоя єдина роль — надавати фактичну інформацію або ставити уточнюючі запитання.

СУВОРА ЗАБОРОНА:
- Якщо це ПЕРШЕ повідомлення в діалозі — можна коротке привітання
- В усіх наступних повідомленнях ЗАБОРОНЕНО будь-які привітання
- ЖОДНИХ вступних фраз ("Дякую за запитання", "Щодо вашого запиту" тощо).
- Одразу пиши суть.

Приклади:
Користувач: "Який контактний телефон?"
Твій варіант: "Уточніть, будь ласка, чий саме номер вас цікавить — Тетяни чи компанії?"

Користувач: "Яка ставка?"
Твій варіант: "Яка сума передбачена в межах даної вакансії?"

Тон: нейтральний, діловий, максимально короткий (до 2 речень). Без емоджі.
"""
# ================================
# Flask app
# ================================
app = Flask(__name__)

# ================================
# Response cleaner
# ================================
def clean_response(text: str) -> str:
    forbidden = ["hello", "hi", "good day", "вітаю", "доброго дня"]
    text_lower = text.lower()
    for word in forbidden:
        if text_lower.startswith(word):
            # Split by first comma and take everything after it, or return original if no comma
            parts = text.split(",", 1)
            if len(parts) > 1:
                return parts[1].strip()
            # If no comma but starts with forbidden word, just strip that word
            return text[len(word):].strip().lstrip(",").strip()
    return text

# ================================
# Telegram sender
# ================================
def send_telegram_message(chat_id: int, text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    response = requests.post(url, json=payload, timeout=10)
    logger.info(f"Sending message to {chat_id}: {text}")
    return response.json()

# ================================
# ChatGPT request
# ================================
def ask_chatgpt(user_text: str) -> str:
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_text
                }
            ]
        )

        return response.output_text.strip()

    except Exception as e:
        logger.error(f"ChatGPT error: {e}", exc_info=True)
        return "❌ Помилка при генерації відповіді."

# ================================
# Health check
# ================================
@app.route("/", methods=["GET"])
def index():
    return "✅ Telegram webhook is running", 200

# ================================
# Webhook
# ================================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)

    if not data:
        logger.warning("Empty request body")
        return "No data", 400

    logger.info(f"Incoming update: {data}")

    if "message" not in data:
        return "OK", 200

    message = data["message"]
    chat_id = message["chat"]["id"]
    username = message.get("from", {}).get("username", "unknown")
    text = message.get("text")

    if not text:
        logger.info("Non-text message ignored")
        return "OK", 200

    # 1️⃣ Ask ChatGPT
    reply = ask_chatgpt(text)
    
    # Clean response from unwanted greetings
    reply = clean_response(reply)

    # 2️⃣ Reply to user
    send_telegram_message(chat_id, reply)

    # 3️⃣ Forward to you (if sender is not you)
    if MY_TELEGRAM_ID and chat_id != MY_TELEGRAM_ID:
        forward = (
            f"🔔 <b>New message</b>\n"
            f"👤 @{username}\n"
            f"🆔 <code>{chat_id}</code>\n\n"
            f"📝 {text}"
        )
        send_telegram_message(MY_TELEGRAM_ID, forward)

    return "OK", 200

# ================================
# Run server
# ================================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
