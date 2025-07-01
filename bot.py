import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Load keys from Render's environment
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
BINANCE_API_KEY = os.environ.get("BINANCE_API_KEY", "")      # Optional (read-only)
BINANCE_SECRET_KEY = os.environ.get("BINANCE_SECRET_KEY", "")

def get_btc_price():
    if BINANCE_API_KEY and BINANCE_SECRET_KEY:
        from binance.client import Client
        client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)
        btc_price = client.get_symbol_ticker(symbol="BTCUSDT")
        return float(btc_price["price"])
    else:
        # Fallback to public API if Binance keys aren't set
        import requests
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        return float(requests.get(url).json()["price"])

def start(update: Update, context: CallbackContext):
    update.message.reply_text("🔍 Ask me about BTC price trends!")

def analyze(update: Update, context: CallbackContext):
    price = get_btc_price()
    update.message.reply_text(f"💰 BTC Price: ${price:.2f}")

if __name__ == "__main__":
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, analyze))
    updater.start_polling()
    updater.idle()