
import json
import os
import re
import random
from datetime import datetime
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

TOKEN = "8149532850:AAG4fPQ_L0Imbv2NkA5lQI4SyP-52mpvyLY"
GROUP_CHAT_ID = -4786953733
CHANNEL_ID = -1002593148496
BALANCE_FILE = "user_balances.json"
GMAIL_FILE = "gmail_list.json"

if os.path.exists(BALANCE_FILE):
    with open(BALANCE_FILE, "r") as f:
        user_balances = json.load(f)
        user_balances = {int(k): v for k, v in user_balances.items()}
else:
    user_balances = {}

if os.path.exists(GMAIL_FILE):
    with open(GMAIL_FILE, "r") as f:
        gmail_list = json.load(f)
else:
    gmail_list = []

reply_map = {}
user_withdraw_state = {}
gmail_data_map = {}
request_counter = 0
complete_counter = 0
user_to_group_msg_map = {}

def save_balances():
    with open(BALANCE_FILE, "w") as f:
        json.dump(user_balances, f)

def save_gmail_list():
    with open(GMAIL_FILE, "w") as f:
        json.dump(gmail_list, f)

def main_menu():
    return ReplyKeyboardMarkup(
        [["📩 Gmail Request", "💰 Balance"], ["🏧 Withdraw"]],
        resize_keyboard=True
    )

def payment_options():
    return ReplyKeyboardMarkup(
        [["Bkash", "Nagad", "Mobile Recharge"]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def extract_field(text, label):
    pattern = rf"{label}:\s*(.+?)(?=\n|$)"
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else None

def generate_random_dob():
    year = random.randint(1997, 2004)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    date_obj = datetime(year, month, day)
    return date_obj.strftime("%-d %B %Y")

def generate_random_gender():
    return random.choice(["Male", "Female"])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 স্বাগতম!\n\n📬 একটি Gmail রিকোয়েস্ট করতে নিচের বাটন ব্যবহার করুন।",
        reply_markup=main_menu()
    )

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global request_counter
    user_id = update.message.from_user.id
    user_name = update.message.from_user.full_name
    text = update.message.text.strip()
    balance = user_balances.get(user_id, 0)

    if text == "📩 Gmail Request":
        request_counter += 1
        if gmail_list:
            data = gmail_list.pop(0)
            save_gmail_list()

            name = extract_field(data, "First name")
            email = extract_field(data, "Email")
            password = extract_field(data, "Password")

            if not all([name, email, password]):
                await update.message.reply_text("❌ ইনফরমেশন ফরম্যাট ভুল!")
                return

            dob = generate_random_dob()
            gender = generate_random_gender()

            msg = (
                f"{request_counter}. 👤 First name: `{name}`\n"
                f"✖️ Last name: `✖️`\n"
                f"📧 Gmail: `{email}`\n"
                f"🔐 Password: `{password}`\n"
                f"🎂 Date of birth: `{dob}`\n"
                f"⚥ Gender: `{gender}`\n\n"
                f"একাউন্ট টি খুলা হয়ে গেলে লগ আউট করে দিন,ধন্যবাদ😊"
            )

            gmail_data_map[user_id] = {
                "name": name,
                "email": email,
                "password": password
            }

            group_msg = await context.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                text=f"Gmail sent to {user_name} (ID: {user_id}):\n\n{msg}",
                parse_mode="Markdown"
            )
            user_to_group_msg_map[user_id] = group_msg.message_id

            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📋 Copy name", callback_data=f"copy_name:{user_id}"),
                    InlineKeyboardButton("📋 Copy email", callback_data=f"copy_email:{user_id}"),
                    InlineKeyboardButton("📋 Copy password", callback_data=f"copy_password:{user_id}")
                ],
                [InlineKeyboardButton("✅ Done ✅", callback_data=f"done:{user_id}:0")]
            ])

            await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=buttons)
        else:
            await update.message.reply_text(
                "প্রিয় মেম্বার, বর্তমানে জিমেইল পাঠানো সম্ভব হচ্ছে না দয়া করে একটু পর আবার চেষ্টা করুন😊"
            )

    elif text == "💰 Balance":
        await update.message.reply_text(f"💼 আপনার ব্যালেন্স: *{balance} টাকা*", parse_mode="Markdown")

    elif text == "🏧 Withdraw":
        if balance >= 225:
            user_withdraw_state[user_id] = "awaiting_method"
            await update.message.reply_text("💳 কোন পেমেন্ট মেথড ব্যবহার করতে চান?", reply_markup=payment_options())
        else:
            await update.message.reply_text("🚫 উইথড্র করার জন্য অন্তত ২২৫ টাকা ব্যালেন্স থাকতে হবে।")

    elif text in ["Bkash", "Nagad", "Mobile Recharge"]:
        if user_withdraw_state.get(user_id) == "awaiting_method":
            user_withdraw_state[user_id] = f"awaiting_number:{text.lower()}"
            await update.message.reply_text(f"📱 অনুগ্রহ করে আপনার {text} নাম্বারটি দিন:")

    elif re.fullmatch(r'01[0-9]{9}', text) and user_id in user_withdraw_state:
        current_state = user_withdraw_state[user_id]
        if current_state.startswith("awaiting_number"):
            method = current_state.split(":")[1].capitalize()
            await update.message.reply_text("✅ উইথড্র রিকোয়েস্ট গ্রহণ করা হয়েছে!\n🕐 ২৪ ঘন্টার মধ্যে প্রক্রিয়া সম্পন্ন হবে।", reply_markup=main_menu())
            await context.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                text=f"📄 Withdraw Request:\n👤 {user_name}\n🆔 ID: {user_id}\n💳 Method: {method}\n📱 Number: {text}\n💰 Amount: {balance} টাকা"
            )
            user_balances[user_id] = 0
            save_balances()
            del user_withdraw_state[user_id]

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global complete_counter
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("done:"):
        parts = data.split(":")
        user_id = int(parts[1])
        if query.from_user.id != user_id:
            await query.edit_message_text("🚫 আপনি এই বাটন ব্যবহার করতে পারবেন না।")
            return
        user_balances[user_id] = user_balances.get(user_id, 0) + 15
        save_balances()
        complete_counter += 1

        await query.edit_message_text(
            text="✅ ধন্যবাদ! আপনার ব্যালেন্সে *১৫ টাকা* যোগ হয়েছে।\n⚠️ সঠিকভাবে ব্যবহারে না করলে ব্যালেন্স *কেটে নেওয়া* হবে।",
            parse_mode="Markdown"
        )

        user_name = query.from_user.full_name
        notify_text = f"{complete_counter}. ✅ Gmail completed by:\n👤 {user_name}\n🆔 ID: {user_id}\n💳 New Balance: {user_balances[user_id]} টাকা"
        reply_to = user_to_group_msg_map.get(user_id)
        if reply_to:
            await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=notify_text, reply_to_message_id=reply_to)
        else:
            await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=notify_text)

        if user_balances[user_id] == 225:
            await context.bot.send_message(chat_id=user_id, text="🎉 অভিনন্দন! আপনি এখন Withdraw করার জন্য ইলিজিবল 💸")

    elif data.startswith("copy_"):
        kind, uid = data.split(":")
        uid = int(uid)
        info = gmail_data_map.get(uid, {})
        key = kind.split("_")[1]
        value = info.get(key)
        if key == "email" and value:
            value = value.split("@")[0]
        if value:
            await query.message.reply_text(value)

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.channel_post.text
    if "First name" in text and "Email" in text and "Password" in text:
        gmail_list.append(text)
        save_gmail_list()

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_user_message))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.CHANNEL, handle_channel_post))
    app.add_handler(CallbackQueryHandler(handle_callback))
    print("🚀 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
