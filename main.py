# main.py
from flask import Flask, request
import os
from telegram import Bot
import openai

# -----------------------------
# 1️⃣ Налаштування змінних середовища
# -----------------------------
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PORT = int(os.environ.get("PORT", 5000))  # Render/Railway/Replit видають PORT через env

bot = Bot(token=TELEGRAM_BOT_TOKEN)
openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

# -----------------------------
# 2️⃣ Маршрут Webhook для Telegram
# -----------------------------
@app.route(f"/webhook/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.json

    # Перевірка чи надійшло повідомлення
    if "message" not in data:
        return {"ok": True}

    chat_id = data["message"]["chat"]["id"]
    user_text = data["message"]["text"]

    # -----------------------------
    # 3️⃣ Виклик OpenAI API
    # -----------------------------
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # або gpt-5-nano, якщо доступно
            messages=[{"role": "user", "content": user_text}]
        )
        answer = response["choices"][0]["message"]["content"]
    except Exception as e:
        answer = "Вибач, сталася помилка 🤖"

    # -----------------------------
    # 4️⃣ Надсилаємо відповідь користувачу
    # -----------------------------
    bot.send_message(chat_id=chat_id, text=answer)
    return {"ok": True}

# -----------------------------
# 5️⃣ Запуск Flask-сервера
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
