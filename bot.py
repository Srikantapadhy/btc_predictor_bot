import logging
import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
import requests
import pandas as pd
import ta

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fetch live BTC data
def fetch_btc_data(interval='5m', limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval={interval}&limit={limit}"
    data = requests.get(url).json()
    df = pd.DataFrame(data, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base', 'taker_buy_quote', 'ignore'
    ])
    df['close'] = pd.to_numeric(df['close'])
    return df

# Predict using RSI
def analyze_btc(interval):
    df = fetch_btc_data(interval)
    df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
    latest_rsi = df['rsi'].iloc[-1]
    price = df['close'].iloc[-1]

    if latest_rsi > 70:
        signal = "🔻 Overbought – Likely to go down"
    elif latest_rsi < 30:
        signal = "🔺 Oversold – Likely to go up"
    else:
        signal = "⚖️ Neutral trend"

    return f"📉 Interval: {interval}\n💰 Price: {price:.2f}\n📊 RSI: {latest_rsi:.2f}\n🧠 Signal: {signal}"

# /btc_5, /btc_10, /btc_15 handlers
async def btc_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    interval = update.message.text.replace("/btc_", "") + "m"
    result = analyze_btc(interval)
    await update.message.reply_text(result)

# /probo handler
async def probo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = analyze_btc('15m')
    await update.message.reply_text("🧠 Probo Prediction:\n" + result)

# Start command with buttons
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("BTC 5m", callback_data='/btc_5')],
        [InlineKeyboardButton("BTC 10m", callback_data='/btc_10')],
        [InlineKeyboardButton("BTC 15m", callback_data='/btc_15')],
        [InlineKeyboardButton("Probo Prediction", callback_data='/probo')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🚀 Welcome! Choose a prediction type:", reply_markup=reply_markup)

# Handle button clicks
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cmd = query.data
    fake_update = Update(update.update_id, message=query.message)
    if cmd == "/probo":
        await probo(fake_update, context)
    else:
        await btc_handler(fake_update, context)

# Main app
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("btc_5", btc_handler))
    app.add_handler(CommandHandler("btc_10", btc_handler))
    app.add_handler(CommandHandler("btc_15", btc_handler))
    app.add_handler(CommandHandler("probo", probo))

    from telegram.ext import CallbackQueryHandler
    app.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
