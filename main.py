from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

TOKEN = '8149532850:AAG4fPQ_L0Imbv2NkA5lQI4SyP-52mpvyLY'

# ✅ Sleep Message
SLEEP_MESSAGE = (
    "⏳ দুঃখিত, বর্তমানে কাজটি বন্ধ রয়েছে।\n\n"
    "🕕 সন্ধ্যা ৬টা থেকে রাত ১০টা পর্যন্ত এই বটটি চালু থাকে।\n\n"
    "ধন্যবাদ 😊"
)

# 📩 Reply to any text message with the sleep message
async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("💤 বট এখন ঘুমাচ্ছে")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(SLEEP_MESSAGE, reply_markup=reply_markup)

# ▶️ Main function
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all_messages))
    print("🤖 Bot is running in sleep mode...")
    app.run_polling()

if __name__ == '__main__':
    main()
