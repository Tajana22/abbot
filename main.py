from flask import Flask, request
from telegram import Bot
import os
from dotenv import load_dotenv

# Завантажуємо змінні з .env
load_dotenv()

# ================================
# Налаштування
# ================================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")   # токен твого бота
MY_TELEGRAM_ID = int(os.getenv("MY_TELEGRAM_ID"))  # твій особистий ID

bot = Bot(token=TELEGRAM_TOKEN)
app = Flask(__name__)

# ================================
# Функція пересилки повідомлення на Telegram
# ================================
def forward_to_telegram(text):
    bot.send_message(chat_id=MY_TELEGRAM_ID, text=text)

# ================================
# Webhook endpoint
# ================================
@app.route(f"/webhook/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"].get("text", "")

        # Пересилання тільки тобі
        forward_to_telegram(f"Повідомлення від користувача {chat_id}: {user_text}")

    return "OK", 200

# ================================
# Запуск Flask (для локальної перевірки)
# ================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
