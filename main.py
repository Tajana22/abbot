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
Ти — ввічливий персональний асистент Тетяни. 

ВАЖЛИВО:
1. Ти НЕ рекрутер і НЕ даєш порад щодо вакансій чи кар'єри. 
2. Ти лише посередник, який збирає інформацію та передає її Тетяні.
3. Відповідай чітко, логічно та по суті повідомлення.

Основні правила:
1. Перше повідомлення (/start): "Hi, there! I'm Tatiana's assistant and I'm glad to help you. For quick communication, you can also use Tatiana's email: naumovat113@gmail.com."
2. Далі в діалозі: НІЯКИХ привітань, email чи фраз "Дякую за повідомлення".
3. Твоя мета — дізнатися: рейт, стек, формат роботи та чи є позиція віддаленою.
4. Спілкуйся природно: "Зрозумів, запишу це для Тетяни", "Добре, я все позначив, Тетяна скоро ознайомиться".
5. Якщо тебе питають про вакансію або просять поради — ввічливо нагадай, що ти лише асистент і передаси всі питання Тетяні.
"""
# ================================
# Flask app
# ================================
app = Flask(__name__)

# ================================
# Response cleaner
# ================================
def clean_response(chat_id: int, text: str) -> str:
    # Check if this is the first assistant message in history
    is_first_reply = True
    if chat_id in chat_history:
        assistant_messages = [m for m in chat_history[chat_id] if m["role"] == "assistant"]
        # If there are already assistant messages, this is NOT the first reply
        if len(assistant_messages) > 1:
            is_first_reply = False

    import re
    clean_text = text.strip()

    if is_first_reply:
        # For the very first reply, we strictly allow only the specific greeting
        # If the text is the hardcoded /start reply, we don't clean it
        if text.strip() == "Hi, there! I'm Tatiana's assistant and I'm glad to help you. For quick communication, you can also use Tatiana's email: naumovat113@gmail.com.":
            return text.strip()
            
    forbidden_greetings = [
        "hello", "hi", "good day", "вітаю", "доброго дня", "привіт", 
        "вітання", "добрий день", "добрий вечір", "доброго вечора", 
        "добрий ранок", "доброго ранку", "thank you for your message", 
        "дякую за ваше повідомлення", "дякую за повідомлення", 
        "дякуємо за ваше повідомлення", "thank you for the message"
    ]
    
    changed = True
    while changed:
        changed = False
        text_lower = clean_text.lower()
        for word in forbidden_greetings:
            if text_lower.startswith(word):
                # Split by punctuation or newline to remove the greeting sentence/phrase
                parts = re.split(r'[,.!?;:\n]', clean_text, maxsplit=1)
                if len(parts) > 1:
                    clean_text = parts[1].strip()
                else:
                    clean_text = clean_text[len(word):].strip().lstrip(",.!?").strip()
                changed = True
                break
                
    return clean_text

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

    # Handle /start command directly
    if text.strip() == "/start":
        reply = "Hi, there! I'm Tatiana's assistant and I'm glad to help you. For quick communication, you can also use Tatiana's email: naumovat113@gmail.com."
        if chat_id not in chat_history:
            chat_history[chat_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
        chat_history[chat_id].append({"role": "user", "content": text})
        chat_history[chat_id].append({"role": "assistant", "content": reply})
        send_telegram_message(chat_id, reply)
        return "OK", 200

    # 1️⃣ Ask ChatGPT
    reply = ask_chatgpt(chat_id, text)
    
    # Clean response from unwanted greetings (allow only for the first reply)
    reply = clean_response(chat_id, reply)

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
    # Use threaded=True to handle multiple incoming requests better
    app.run(host="0.0.0.0", port=port, threaded=True)
