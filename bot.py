import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ✅ Load .env from 'key.env'
load_dotenv(dotenv_path="key.env")

# ✅ Get tokens from env
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

# ✅ Debug check
if not TELEGRAM_TOKEN:
    raise ValueError("🚫 TELEGRAM_TOKEN not found in key.env")

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is working! Try /btc_5 for prediction.")

async def btc_5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 BTC 5-min prediction placeholder.")

async def btc_10(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 BTC 10-min prediction placeholder.")

async def btc_15(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 BTC 15-min prediction placeholder.")

async def probo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Ask your Probo-style BTC question:\nWill BTC cross 68k tonight?")

# --- Main App ---
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("btc_5", btc_5))
    app.add_handler(CommandHandler("btc_10", btc_10))
    app.add_handler(CommandHandler("btc_15", btc_15))
    app.add_handler(CommandHandler("probo", probo))

    print("✅ Bot is running with TELEGRAM_TOKEN from key.env")
    app.run_polling()

if __name__ == '__main__':
    main()
