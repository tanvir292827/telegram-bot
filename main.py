import json
import os
import re
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TOKEN = '8149532850:AAG4fPQ_L0Imbv2NkA5lQI4SyP-52mpvyLY'
GROUP_CHAT_ID = -4786953733
BALANCE_FILE = 'user_balances.json'

if os.path.exists(BALANCE_FILE):
    with open(BALANCE_FILE, 'r') as f:
        user_balances = json.load(f)
        user_balances = {int(k): v for k, v in user_balances.items()}
else:
    user_balances = {}

reply_map = {}
user_withdraw_state = {}
gmail_data_map = {}

def save_balances():
    with open(BALANCE_FILE, 'w') as f:
        json.dump(user_balances, f)

def main_menu():
    return ReplyKeyboardMarkup(
        [
            ["📩 Get a Gmail", "💰 Balance"],
            ["🏧 Withdraw"]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

def payment_options():
    return ReplyKeyboardMarkup(
        [["Bkash", "Nagad", "📱 Mobile Recharge"]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 স্বাগতম! নিচের বাটনে ক্লিক করে একটি Gmail রিকোয়েস্ট পাঠান।",
        reply_markup=main_menu()
    )

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.full_name
    text = update.message.text.strip()
    balance = user_balances.get(user_id, 0)

    if text == "📩 Get a Gmail":
        sent = await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"📨 Gmail request from:
👤 {user_name}
🆔 User ID: {user_id}"
        )
        reply_map[sent.message_id] = user_id
        await update.message.reply_text("📥 অনুগ্রহ করে অপেক্ষা করুন, অ্যাডমিন ম্যানুয়ালি Gmail পাঠাবেন...")

    elif text == "💰 Balance":
        await update.message.reply_text(f"💰 আপনার ব্যালেন্স: {balance} টাকা")

    elif text == "🏧 Withdraw":
        if balance >= 225:
            user_withdraw_state[user_id] = "awaiting_method"
            await update.message.reply_text("💳 কোন পেমেন্ট মেথডে উইথড্র করতে চান?", reply_markup=payment_options())
        else:
            await update.message.reply_text("❌ উইথড্র করার জন্য অন্তত ২২৫ টাকা ব্যালেন্স থাকতে হবে।")

    elif text in ["Bkash", "Nagad", "📱 Mobile Recharge"]:
        if user_withdraw_state.get(user_id) == "awaiting_method":
            user_withdraw_state[user_id] = f"awaiting_number:{text.lower()}"
            await update.message.reply_text(f"আপনার {text} নাম্বারটি লিখুন✍️")

    elif re.fullmatch(r'01[0-9]{9}', text) and user_id in user_withdraw_state:
        current_state = user_withdraw_state[user_id]
        if current_state.startswith("awaiting_number"):
            method = current_state.split(":")[1].capitalize()
            await update.message.reply_text(
                "✅ আপনার Withdraw টি পেন্ডিং এ রয়েছে, ২৪ ঘন্টার মধ্যে ব্যালেন্স আপনার একাউন্ট এ জমা হয়ে যাবে,ধন্যবাদ🌺",
                reply_markup=main_menu()
            )
            await context.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                text=f"📤 Withdraw Request:
👤 {user_name}
🆔 ID: {user_id}
💳 Method: {method}
📱 Number: {text}
💰 Amount: {balance} টাকা"
            )
            user_balances[user_id] = 0
            save_balances()
            del user_withdraw_state[user_id]

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("copy_"):
        field, user_id = data.split(":")
        user_id = int(user_id)
        info = gmail_data_map.get(user_id, {})
        key = field.replace("copy_", "")
        value = info.get(key)
        if value:
            await query.message.reply_text(value)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_user_message))
    app.add_handler(CallbackQueryHandler(handle_callback))
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
