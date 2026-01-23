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

# Store chat history
chat_history = {}

# ================================
# System prompt (Recruiter assistant)
# ================================
SYSTEM_PROMPT = """
Ти — персональний асистент Тетяни. Твоє завдання — приймати вхідні повідомлення та запити від рекрутерів.

Ти НЕ є Тетяна і НЕ відповідаєш від її імені. Ти дієш виключно як посередник, який збирає інформацію.

Жорсткі правила:
- Заборонено використовувати "я", "мені", "мене" від імені Тетяни.
- Завжди відповідай як асистент: "Я зафіксував ваш запит", "Передам інформацію Тетяні", "Тетяна ознайомиться з пропозицією".
- Ніколи не імітуй особисті думки Тетяни.
- Не починай з привітань.
- Чітко зазначай свою роль асистента.

Формат відповідей:
- 1–3 короткі речення.
- Діловий, нейтральний стиль.
- Одразу по суті.

Мета:
- Прийняти пропозицію від рекрутера.
- Уточнити технічні деталі (рейт, стек, формат), щоб передати їх Тетяні в повному обсязі.
- Повідомити, що інформацію буде передано для ознайомлення.

Приклади:
"Ваш запит прийнято. Передам Тетяні деталі вакансії для ознайомлення."
"Інформацію зафіксовано. Уточніть, будь ласка, бюджет вакансії та стек технологій, щоб я міг передати повні дані Тетяні."

Якщо повідомлення не стосується роботи — відповідай коротко, що асистент приймає лише ділові пропозиції.
"""
# ================================
# Flask app
# ================================
app = Flask(__name__)

# ================================
# Response cleaner
# ================================
def clean_response(text: str) -> str:
    forbidden = ["hello", "hi", "good day", "вітаю", "доброго дня", "привіт", "вітання", "добрий день", "добрий вечір"]
    text_lower = text.lower().strip()
    
    # Check if any forbidden word is at the very beginning
    for word in forbidden:
        if text_lower.startswith(word):
            # Find the first occurrence of common punctuation or newline after the greeting
            # This ensures we catch "Доброго дня, Тетяна..." or "Вітаю! Тетяна..."
            import re
            # Split by first punctuation mark or newline
            parts = re.split(r'[,.!?;:\n]', text, maxsplit=1)
            if len(parts) > 1:
                return parts[1].strip()
            # If no punctuation but starts with forbidden word, just strip that word
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
def get_messages(chat_id, user_message):
    if chat_id not in chat_history:
        chat_history[chat_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    chat_history[chat_id].append(
        {"role": "user", "content": user_message}
    )

    # Keep only system prompt + last 10 messages
    if len(chat_history[chat_id]) > 11:
        chat_history[chat_id] = [chat_history[chat_id][0]] + chat_history[chat_id][-10:]

    return chat_history[chat_id]

def ask_chatgpt(chat_id: int, user_text: str) -> str:
    try:
        messages = get_messages(chat_id, user_text)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        reply = response.choices[0].message.content.strip()
        
        # Add assistant response to history
        chat_history[chat_id].append({"role": "assistant", "content": reply})
        
        return reply

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
    reply = ask_chatgpt(chat_id, text)
    
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
