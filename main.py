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
Ти — надзвичайно ввічливий персональний асистент Тетяни. 

Твоє завдання — приймати повідомлення від рекрутерів та передавати інформацію Тетяні.

Жорсткі правила:
1. Якщо користувач надсилає команду /start, твоє найперше повідомлення ПОВИННО бути: "Hi, there! I'm Tatiana's assistant and I'm glad to help you."
2. В усіх наступних повідомленнях ЗАБОРОНЕНО використовувати фразу "Дякую за ваше повідомлення" або будь-які її варіації.
3. ПРИВІТАННЯ дозволено ТІЛЬКИ у найпершому повідомленні діалогу. Далі — КАТЕГОРИЧНО ЗАБОРОНЕНО.
4. Спілкуйся у ввічливій та професійній манері.
5. Відповідай лаконічно, продовжуючи контекст.
6. Повідомляй, що ти обов'язково передаси всі деталі Тетяні. Для швидкої комунікації можна також використовувати email Тетяни: naumovat113@gmail.com.
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
        if len(assistant_messages) > 1:
            is_first_reply = False

    import re
    clean_text = text.strip()

    # Remove forbidden thank you phrases from any message except potentially the very first one
    if not is_first_reply:
        thank_you_phrases = [
            "дякую за ваше повідомлення", 
            "дякую за повідомлення", 
            "дякуємо за ваше повідомлення",
            "thank you for your message",
            "thank you for the message"
        ]
        text_lower = clean_text.lower()
        for phrase in thank_you_phrases:
            if text_lower.startswith(phrase):
                parts = re.split(r'[,.!?;:\n]', clean_text, maxsplit=1)
                if len(parts) > 1:
                    clean_text = parts[1].strip()
                else:
                    clean_text = clean_text[len(phrase):].strip().lstrip(",.!?").strip()
                break

    if is_first_reply:
        return clean_text

    forbidden_greetings = ["hello", "hi", "good day", "вітаю", "доброго дня", "привіт", "вітання", "добрий день", "добрий вечір", "доброго вечора", "добрий ранок", "доброго ранку"]
    
    changed = True
    while changed:
        changed = False
        text_lower = clean_text.lower()
        for word in forbidden_greetings:
            if text_lower.startswith(word):
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
        reply = "Hi, there! I'm Tatiana's assistant and I'm glad to help you."
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
    app.run(host="0.0.0.0", port=port)
