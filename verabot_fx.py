import time
import threading
import finnhub
import telebot
import os
from flask import Flask

# === Переменные окружения (Render Environment) ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
FINNHUB_KEY = os.getenv("FINNHUB_KEY")
CHAT_ID = int(os.getenv("CHAT_ID"))
# =================================================

SYMBOL = "OANDA:EUR_USD"

bot = telebot.TeleBot(BOT_TOKEN)
finnhub_client = finnhub.Client(api_key=FINNHUB_KEY)

previous_high = None
previous_low = None

# --- Мини веб-сервер для Render ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!", 200


@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, f"Ваш chat_id: {message.chat.id}")
    bot.send_message(message.chat.id, "Мониторинг EURUSD активирован. Проверка каждые 60 секунд.")


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
            bot.send_message(CHAT_ID, f"📈 Новый HIGH H1: {current_high:.5f}")
            previous_high = current_high

        if current_low < previous_low:
            bot.send_message(CHAT_ID, f"📉 Новый LOW H1: {current_low:.5f}")
            previous_low = current_low

    except Exception as e:
        print("Ошибка в check_price:", e)


def main():
    print("Бот запущен. Проверка каждые 60 секунд.")
    while True:
        try:
            check_price()
            time.sleep(60)
        except Exception as e:
            print("Ошибка:", e)
            time.sleep(60)


def run_bot():
    print("Запуск Telegram polling...")
    bot.infinity_polling(timeout=60, long_polling_timeout=10)


def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    t1 = threading.Thread(target=run_bot)
    t1.start()
    main_thread = threading.Thread(target=main)
    main_thread.start()
    run_flask()

