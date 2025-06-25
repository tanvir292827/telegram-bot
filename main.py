from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# ✅ Bot Token
TOKEN = '7790464127:AAF8WvwEVrx1gpP26AIwZuQ72HgQnobjJSw'

# ✅ Sleep Message (Always shown)
SLEEP_MESSAGE = (
    "⏳ দুঃখিত, বর্তমানে কাজটি বন্ধ রয়েছে।\n\n"
    "🕕 এই বটে কাজ করা হয় সন্ধ্যা ৬ টা থেকে রাত ১০ টা পর্যন্ত।\n\n"
    "অনুগ্রহ করে নির্ধারিত সময়ের মধ্যে মেসেজ করুন।\n\n"
    "ধন্যবাদ 😊"
)

# ✅ Respond to any message
async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(SLEEP_MESSAGE)

# ✅ Main Function
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_reply))  # Reply to all texts
    app.add_handler(MessageHandler(filters.COMMAND, auto_reply))  # Reply to any command too
    print("🤖 Sleep Mode Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
