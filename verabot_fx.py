import asyncio
import json
import requests
import websockets
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "8357685940:AAFXzQgVXJh5XCxvfw2bryDjNX8r-TcI0kw"
FINNHUB_KEY = "d3rkj0pr01qopgh8sfa0d3rkj0pr01qopgh8sfag"
SYMBOL = "OANDA:EUR_USD"

current_high = None
current_low = None
previous_high = None
previous_low = None

async def get_hourly_data():
    url = f"https://finnhub.io/api/v1/forex/candle?symbol={SYMBOL}&resolution=60&count=2&token={FINNHUB_KEY}"
    r = requests.get(url).json()
    if r.get("s") != "ok":
        return None
    return r["h"][-2], r["l"][-2]  # high, low последней закрытой свечи

async def price_stream(chat_id, context: ContextTypes.DEFAULT_TYPE):
    global current_high, current_low
    async with websockets.connect(f"wss://ws.finnhub.io?token={FINNHUB_KEY}") as ws:
        await ws.send(json.dumps({"type": "subscribe", "symbol": SYMBOL}))
        while True:
            msg = json.loads(await ws.recv())
            if "data" in msg:
                price = msg["data"][0]["p"]
                if current_high and price > current_high:
                    await context.bot.send_message(chat_id=chat_id, text=f"🔺 Снятие ликвидности выше H1 high: {price:.5f}")
                    current_high = price
                elif current_low and price < current_low:
                    await context.bot.send_message(chat_id=chat_id, text=f"🔻 Снятие ликвидности ниже H1 low: {price:.5f}")
                    current_low = price

async def candle_check(context: ContextTypes.DEFAULT_TYPE):
    global current_high, current_low, previous_high, previous_low
    data = await get_hourly_data()
    if not data:
        return
    high, low = data
    if previous_high is None:
        previous_high, previous_low = high, low
        current_high, current_low = high, low
        return
    if high > previous_high:
        await context.bot.send_message(chat_id=context.job.chat_id, text=f"📈 Новый HIGH H1: {high:.5f}")
    if low < previous_low:
        await context.bot.send_message(chat_id=context.job.chat_id, text=f"📉 Новый LOW H1: {low:.5f}")
    previous_high, previous_low = high, low
    current_high, current_low = high, low

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text("Мониторинг EURUSD активирован. Будут уведомления о закрытии H1 и пробоях уровней.")
    context.job_queue.run_repeating(candle_check, interval=3600, first=5, chat_id=chat_id)
    asyncio.create_task(price_stream(chat_id, context))

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
