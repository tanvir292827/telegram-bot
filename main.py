import json
import os
import re
import asyncio
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = 'PASTE_YOUR_BOT_TOKEN_HERE'
GROUP_CHAT_ID = -1001234567890  # Replace with your private group ID
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

async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        original_msg_id = update.message.reply_to_message.message_id
        user_info = reply_map.get(original_msg_id)
        if user_info:
            user_id = user_info if isinstance(user_info, int) else user_info["user_id"]
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Done", callback_data=f"done:{user_id}:{update.message.message_id}")]
            ])
            await context.bot.send_message(
                chat_id=user_id,
                text=update.message.text,
                reply_markup=keyboard
            )
            reply_map[original_msg_id] = {
                "user_id": user_id,
                "admin_msg_id": update.message.message_id
            }

async def handle_done_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("done:"):
        parts = data.split(":")
        user_id = int(parts[1])
        admin_msg_id = int(parts[2]) if len(parts) > 2 else None

        if query.from_user.id != user_id:
            await query.edit_message_text("❌ আপনি এই বাটন ব্যবহার করতে পারবেন না।")
            return

        user_balances[user_id] = user_balances.get(user_id, 0) + 15
        save_balances()

        await query.edit_message_text(
            text="✅ ধন্যবাদ! আপনার ব্যালেন্সে ১৫ টাকা যোগ হয়েছে।
⚠️ সতর্কতা: আপনাকে প্রদান করা জিমেইলটি সঠিকভাবে *রেজিষ্ট্রেশন* এবং *লগআউট* না করা হলে, ব্যালেন্স *কেটে নেওয়া* হবে।",
            parse_mode="Markdown"
        )

        user_name = query.from_user.full_name
        notify_text = f"✅ Gmail completed by:
👤 {user_name}
🆔 User ID: {user_id}
💳 Current Balance: {user_balances[user_id]} টাকা"

        if admin_msg_id:
            await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=notify_text, reply_to_message_id=admin_msg_id)
        else:
            await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=notify_text)

        if user_balances[user_id] == 225:
            await context.bot.send_message(
                chat_id=user_id,
                text="🎉 অভিনন্দন! আপনি এখন Withdraw করার জন্য ইলিজিবল💸"
            )

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_user_message))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_admin_reply))
    app.add_handler(CallbackQueryHandler(handle_done_callback))
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
