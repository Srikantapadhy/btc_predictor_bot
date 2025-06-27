import os
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests
import pandas as pd
from dotenv import load_dotenv
from indicators import get_rsi

load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API keys
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Binance API URL
BASE_URL = "https://api.binance.com"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("BTC in 5 min", callback_data='btc_5')],
        [InlineKeyboardButton("BTC in 10 min", callback_data='btc_10')],
        [InlineKeyboardButton("BTC in 15 min", callback_data='btc_15')],
        [InlineKeyboardButton("Probo Style", callback_data='probo')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome to Probo Predictor! Choose a prediction:", reply_markup=reply_markup)

def get_binance_ohlc(interval='1m', limit=50):
    url = f"{BASE_URL}/api/v3/klines?symbol=BTCUSDT&interval={interval}&limit={limit}"
    res = requests.get(url)
    data = res.json()
    df = pd.DataFrame(data, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
        'quote_asset_volume', 'num_trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'
    ])
    df['close'] = df['close'].astype(float)
    return df

def predict_price(interval='1m'):
    df = get_binance_ohlc(interval)
    rsi = get_rsi(df)

    if rsi > 70:
        signal = "🔻 BTC is likely to go DOWN (Overbought)"
    elif rsi < 30:
        signal = "🔺 BTC is likely to go UP (Oversold)"
    else:
        signal = "⏸ BTC may move sideways (Neutral RSI)"

    current_price = df['close'].iloc[-1]
    change = round(abs(df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2] * 100, 2)
    return f"{signal}\nCurrent Price: {current_price:.2f} USDT\nExpected Change: ±{change}%"

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    interval = query.data

    if interval == 'btc_5':
        msg = predict_price('1m')
    elif interval == 'btc_10':
        msg = predict_price('3m')
    elif interval == 'btc_15':
        msg = predict_price('5m')
    elif interval == 'probo':
        msg = predict_price('1m')  # You can customize this more

    await query.edit_message_text(f"🕒 {interval.upper()} Prediction:\n\n{msg}")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("btc", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("probo", start))
    app.add_handler(CommandHandler("btc_5", start))
    app.add_handler(CommandHandler("btc_10", start))
    app.add_handler(CommandHandler("btc_15", start))
    app.add_handler(telegram.ext.CallbackQueryHandler(button_handler))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()