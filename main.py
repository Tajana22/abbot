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
Ти — Тетяна, і ти зараз активно шукаєш роботу. Ти НЕ рекрутер. Твоє завдання — відповідати рекрутерам, які пишуть тобі з пропозиціями.

Спілкуйся як жива людина, простою мовою, без офіціозу.

ОСНОВНІ ПРАВИЛА:
1. Пиши від першої особи (я, мені, мій).
2. Чітко давай зрозуміти, що ти — кандидат, який шукає нові можливості.
3. ЖОДНИХ шаблонних привітань ("Доброго дня", "Вітаю") та вступних кліше ("Дякую за пропозицію").
4. Відповідай одразу по суті.
5. Твоя мета — дізнатися ключові деталі: чи це повний ремоут, який стек технологій та який бюджет (рейт) вакансії.
6. Будь лаконічною: 1-2 речення.

Приклади:
"Якраз шукаю нові проекти. Підкажіть, чи можливий повний ремоут і який стек використовуєте?"
"Цікаво дізнатися деталі. Який рейт передбачений для цієї позиції?"
"""
# ================================
# Flask app
# ================================
app = Flask(__name__)

# ================================
# Response cleaner
# ================================
def clean_response(text: str) -> str:
    forbidden = ["hello", "hi", "good day", "вітаю", "доброго дня", "привіт"]
    text_lower = text.lower().strip()
    
    # Check if the text starts with any forbidden word followed by optional punctuation
    for word in forbidden:
        if text_lower.startswith(word):
            # Find the first occurrence of common separators after the greeting
            # We look for comma, period, exclamation mark or newline
            first_comma = text.find(",")
            first_period = text.find(".")
            first_exclamation = text.find("!")
            first_newline = text.find("\n")
            
            # Find the earliest separator
            separators = [s for s in [first_comma, first_period, first_exclamation, first_newline] if s != -1]
            
            if separators:
                split_at = min(separators)
                # If it's a comma, we skip it. For others, we might want to keep them or skip
                # Usually greetings are followed by a comma or a period/exclamation
                return text[split_at + 1:].strip()
            
            # If no separator found but starts with word, just strip the word
            return text[len(word):].strip().lstrip(",.!?").strip()
            
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
