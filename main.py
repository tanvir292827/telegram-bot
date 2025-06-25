
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = '8149532850:AAG4fPQ_L0Imbv2NkA5lQI4SyP-52mpvyLY'

app = Flask(__name__)

# Telegram Bot Message
SLEEP_MESSAGE = (
    "⏳ দুঃখিত, বর্তমানে কাজটি বন্ধ রয়েছে।

"
    "🕕 সন্ধ্যা ৬টা থেকে রাত ১০টা পর্যন্ত এই বটে কাজ করা হয়।

"
    "ধন্যবাদ😊"
)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(SLEEP_MESSAGE)

# All messages
async def all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(SLEEP_MESSAGE)

def run_bot():
    app_bot = ApplicationBuilder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, all_messages))
    print("🤖 Bot is running...")
    app_bot.run_polling()

@app.route('/')
def home():
    return "Bot is alive!"

if __name__ == '__main__':
    run_bot()
