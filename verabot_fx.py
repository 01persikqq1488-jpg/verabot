import telebot
import finnhub
import time
import os
import threading
from flask import Flask

# --- Настройки окружения ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
FINNHUB_KEY = os.getenv("FINNHUB_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
finnhub_client = finnhub.Client(api_key=FINNHUB_KEY)
app = Flask(__name__)

SYMBOL = "OANDA:EUR_USD"
previous_high = None
previous_low = None

# === Работа с подписчиками ===
SUBSCRIBERS_FILE = "subscribers.txt"

# загрузка подписчиков из файла
def load_subscribers():
    if not os.path.exists(SUBSCRIBERS_FILE):
        return set()
    with open(SUBSCRIBERS_FILE, "r") as f:
        return set(int(line.strip()) for line in f if line.strip().isdigit())

# сохранение подписчиков в файл
def save_subscribers(subscribers):
    with open(SUBSCRIBERS_FILE, "w") as f:
        for chat_id in subscribers:
            f.write(str(chat_id) + "\n")

subscribers = load_subscribers()

# === Telegram команды ===
@app.route('/')
def home():
    return "Bot is running", 200

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.chat.id
    if user_id not in subscribers:
        subscribers.add(user_id)
        save_subscribers(subscribers)
        bot.reply_to(message, "✅ Вы подписаны на уведомления EUR/USD (H1).")
        print(f"[+] Новый пользователь: {user_id}")
    else:
        bot.reply_to(message, "Вы уже подписаны.")

@bot.message_handler(commands=['stop'])
def stop_command(message):
    user_id = message.chat.id
    if user_id in subscribers:
        subscribers.remove(user_id)
        save_subscribers(subscribers)
        bot.reply_to(message, "❌ Вы отписались от уведомлений.")
        print(f"[-] Пользователь удалён: {user_id}")
    else:
        bot.reply_to(message, "Вы не были подписаны.")_

