import time
import finnhub
import telebot
import os

# === ВАШИ ДАННЫЕ ===
BOT_TOKEN = "8357685940:AAFzQ9VXJh5XCxvfw2bryDjNX8r-TcIOkw"
FINNHUB_KEY = "d3rkj9kp0pr01qopqph8sfa0d3rkj9kp0pr01qopqph8sfag"
CHAT_ID = 6486928282
# ====================

SYMBOL = "OANDA:EUR_USD"

bot = telebot.TeleBot(BOT_TOKEN)
finnhub_client = finnhub.Client(api_key=FINNHUB_KEY)

previous_high = None
previous_low = None


@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, f"Ваш chat_id: {message.chat.id}")
    bot.send_message(message.chat.id, "Мониторинг EURUSD активирован. Проверка каждые 60 секунд.")


def check_price():
    global previous_high, previous_low

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


def main():
    print("Бот запущен. Проверка каждые 60 секунд.")
    while True:
        try:
            check_price()
            time.sleep(60)
        except Exception as e:
            print("Ошибка:", e)
            time.sleep(60)


if __name__ == "__main__":
    import threading
    t = threading.Thread(target=main)
    t.start()
    bot.infinity_polling()
