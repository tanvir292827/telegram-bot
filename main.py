
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# ✅ Bot Token
TOKEN = '8149532850:AAG4fPQ_L0Imbv2NkA5lQI4SyP-52mpvyLY'

# ✅ Sleep Message (Always)
SLEEP_MESSAGE = (
    "⏳ দুঃখিত, বর্তমানে কাজটি বন্ধ রয়েছে।\n\n"
    "🕕 প্রতিদিন সন্ধ্যা ৬ টা থেকে রাত ১০ টা পর্যন্ত এই বটে কাজ করা হয়।\n\n"
    "ধন্যবাদ 😊"
)

# ✅ Message Handler (any text)
async def sleep_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(SLEEP_MESSAGE)

# ✅ Main function
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, sleep_reply))
    print("🤖 Sleep-mode bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
