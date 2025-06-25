from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# ✅ Bot Token
TOKEN = '8149532850:AAG4fPQ_L0Imbv2NkA5lQI4SyP-52mpvyLY'

# ✅ Sleep Message
SLEEP_MESSAGE = (
    "⏳ দুঃখিত, বর্তমানে কাজটি বন্ধ রয়েছে।\n\n"
    "🕕 কাজের সময়: সন্ধ্যা ৬ টা থেকে রাত ১০ টা পর্যন্ত।\n\n"
    "🙏 অনুগ্রহ করে নির্ধারিত সময়ের মধ্যে মেসেজ করুন।\n\n"
    "ধন্যবাদ 😊"
)

# ✅ /start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(SLEEP_MESSAGE)

# ✅ Auto reply to any message
async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(SLEEP_MESSAGE)

# ✅ Main function
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_reply))
    print("🤖 Bot is running in SLEEP MODE...")
    app.run_polling()

if __name__ == '__main__':
    main()
