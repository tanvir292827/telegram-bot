import json
import os
import re
import random
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

TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
GROUP_CHAT_ID = -1001234567890
BALANCE_FILE = 'user_balances.json'

if os.path.exists(BALANCE_FILE):
    with open(BALANCE_FILE, 'r') as f:
        user_balances = json.load(f)
        user_balances = {int(k): v for k, v in user_balances.items()}
else:
    user_balances = {}

reply_map = {}
user_withdraw_state = {}

def save_balances():
    with open(BALANCE_FILE, 'w') as f:
        json.dump(user_balances, f)

def main_menu():
    return ReplyKeyboardMarkup(
        [["📩 Get a Gmail", "💰 Balance"], ["🏧 Withdraw"]],
        resize_keyboard=True
    )

def payment_options():
    return ReplyKeyboardMarkup(
        [["Bkash", "Nagad", "📱 Mobile Recharge"]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def generate_gmail_info():
    first_name = random.choice(["Rafi", "Mehedi", "Tarek", "Shanto"])
    email_user = ''.join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=10))
    email = f"{email_user}@gmail.com"
    password = ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789", k=12))
    dob = f"{random.randint(1997, 2004)}-{random.randint(1,12):02}-{random.randint(1,28):02}"
    gender = random.choice(["Male", "Female"])
    return first_name, email_user, email, password, dob, gender

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
        first, local_part, email, pwd, dob, gender = generate_gmail_info()
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 Copy Name", callback_data=f"copy_name:{first}")],
            [InlineKeyboardButton("📋 Copy Email", callback_data=f"copy_email:{local_part}")],
            [InlineKeyboardButton("📋 Copy Password", callback_data=f"copy_password:{pwd}")]
        ])
        message = f"""First Name: `{first}`
Last Name: ✖️
Email: `{email}`
Password: `{pwd}`
Gender: {gender}
Date of Birth: {dob}

একাউন্ট টি খুলা হয়ে গেলে লগ আউট করে দিন,ধন্যবাদ😊"""
        await update.message.reply_text(message, parse_mode="Markdown", reply_markup=keyboard)

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

async def handle_copy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("copy_"):
        _, field = data.split("_", 1)
        label, value = field.split(":", 1)
        await query.message.reply_text(f"📋 কপি হয়েছে: `{value}`", parse_mode="Markdown")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_user_message))
    app.add_handler(CallbackQueryHandler(handle_copy_callback, pattern="^copy_"))
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
