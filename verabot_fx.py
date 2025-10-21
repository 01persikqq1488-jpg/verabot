import os
import time
import threading
import telebot
import finnhub
from flask import Flask

BOT_TOKEN = os.getenv("BOT_TOKEN")
FINNHUB_KEY = os.getenv("FINNHUB_KEY")

SYMBOL = "OANDA:EUR_USD"
SUBSCRIBERS_FILE = "subscribers.txt"

bot = telebot.TeleBot(BOT_TOKEN)
finnhub_client = finnhub.Client(api_key=FINNHUB_KEY)
previous_high = None
previous_low = None

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running", 200


def load_subscribers():
    if not os.path.exists(SUBSCRIBERS_FILE):
        return set()
    with open(SUBSCRIBERS_FILE, "r") as f:
        return set(int(line.strip()) for line in f if line.strip().isdigit())

def save_subscribers(subscribers):
    with open(SUBSCRIBERS_FILE, "w") as f:
        for chat_id in subscribers:
            f.write(str(chat_id) + "\n")

subscribers = load_subscribers()


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
        bot.reply_to(message, "Вы не были подписаны.")


def check_price():
    global previous_high, previous_low
    try:
        candles = finnhub_client.forex_candles(SYMBOL, '60', int(time.time()) - 60*60*24, int(time.time()))
        if candles['s'] != 'ok':
            print("Ошибка получения данных от Finnhub")
            return

        highs = candles['h']
        lows = candles['l']
        current_high = highs[-1]
        current_low = lows[-1]

        if previous_high is None or previous_low is None:
            previous_high = current_high
            previous_low = current_low
            return

        if current_high > previous_high:
            for chat_id in subscribers:
                bot.send_message(chat_id, f"📈 Новый HIGH H1




