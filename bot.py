import requests
import random
import json
import time
import threading
import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, CallbackContext

# ---------------------- CONFIGURATION ----------------------

TOKEN = os.getenv("7881208281:AAGR8DAaGV2s2AvyquL95h90ZMVPB11Q8RM")  # Use Railway environment variable
BASE_URL = "https://boats-app-cba6ae7713ab.herokuapp.com"
RAILWAY_URL = os.getenv("https://web-production-b9df3.up.railway.app/bot.py")  # Your Railway app’s public URL

DATA_FILE = "users.json"
ALLOWED_USERS = ["6735321947", "2120592843"]  # Replace with allowed Telegram user IDs

# Initialize Flask app
app = Flask(__name__)

# Initialize Telegram Bot
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)
running_cycles = {}

# ---------------------- LOAD & SAVE USER DATA ----------------------

def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=4)

users = load_users()

# ---------------------- TELEGRAM BOT FUNCTIONS ----------------------

def send_request(name, url, data=None, method="POST"):
    session = requests.Session()
    headers = {
        "currency": "USD",
        "Connection": "close",
        "rentappsetup": "true",
        "version": "2.7",
        "language": "English",
        "packageName": "com.boat.app.adventure",
        "versionCode": "27",
        "storeType": "google_play",
        "authcode": data.get("auth", ""),
        "Content-Type": "application/json; charset=utf-8",
        "Accept-Encoding": "gzip",
        "User-Agent": "okhttp/5.0.0-alpha.14"
    }
    response = session.post(url, headers=headers, json=data) if method == "POST" else session.get(url)
    try:
        return json.dumps(response.json(), indent=4)
    except json.JSONDecodeError:
        return response.text

def start(update: Update, context: CallbackContext):
    update.message.reply_text("✅ Welcome! Use /setver to set your verification codes.")

def set_verification(update: Update, context: CallbackContext):
    user_id = str(update.message.chat_id)
    if user_id not in ALLOWED_USERS:
        update.message.reply_text("❌ You are not authorized.")
        return

    if len(context.args) < 2:
        update.message.reply_text("⚠️ Usage: /setver <create|cycle|end|auth|status> <code>")
        return

    key, value = context.args[0], context.args[1]
    if key not in ["create", "cycle", "end", "auth", "status"]:
        update.message.reply_text("⚠️ Invalid key! Use: create, cycle, end, auth, status.")
        return

    users.setdefault(user_id, {})[key] = value
    save_users(users)
    update.message.reply_text(f"✅ Updated {key} verification code!")

def chk_verification(update: Update, context: CallbackContext):
    user_id = str(update.message.chat_id)
    if user_id not in users:
        update.message.reply_text("⚠️ No verification codes found. Use /setver to add.")
        return

    codes = users[user_id]
    message = (
        f"✅ AUTH: {codes.get('auth', 'Not Set')}\n"
        f"✅ Your verification codes:\n"
        f"🔹 Create: {codes.get('create', 'Not Set')}\n"
        f"🔹 Cycle: {codes.get('cycle', 'Not Set')}\n"
        f"🔹 End: {codes.get('end', 'Not Set')}\n"
        f"🔹 Status: {codes.get('status', 'Not Set')}"
    )
    update.message.reply_text(message)

def run_cycle(user_id):
    while running_cycles.get(user_id, False):
        status_url = "https://givvy-general-config.herokuapp.com/getStatus"
        status_data = {"verificationCode": users[user_id]["status"]}
        status_response = send_request("Get Status", status_url, status_data)
        bot.send_message(chat_id=user_id, text=f"✔ Get Status Response: {json.loads(status_response)['statusText']}.")

        reward_url = f"{BASE_URL}/getCycleAdsReward"
        reward_data = {"verificationCode": users[user_id]["cycle"]}
        reward_response = send_request("Get Cycle Ads Reward", reward_url, reward_data)
        bot.send_message(chat_id=user_id, text=f"✔ Get Cycle Ads Reward Response:\n{json.loads(reward_response)['statusText']}.\nYou Earned: {json.loads(reward_response)['result']['earnCredits']}.\nUpdated Credits: {json.loads(reward_response)['result']['credits']}.\nUSD: {json.loads(reward_response)['result']['userBalance']}$.")
        
        time.sleep(10 + random.uniform(0, 5))

    bot.send_message(chat_id=user_id, text="🛑 Cycle stopped.")

def process_cycle(update: Update, context: CallbackContext):
    user_id = str(update.message.chat_id)
    if user_id not in users or not all(k in users[user_id] for k in ["create", "cycle", "end", "auth", "status"]):
        update.message.reply_text("⚠️ Set verification codes first using /setver")
        return

    if running_cycles.get(user_id, False):
        update.message.reply_text("⚠️ A cycle is already running!")
        return

    update.message.reply_text("🔄 Starting process...")
    create_url = f"{BASE_URL}/createNewSession"
    create_data = {"verificationCode": users[user_id]["create"]}
    create_response = send_request("Create New Session", create_url, create_data)
    bot.send_message(chat_id=user_id, text=f"✔ Create New Session Response:\n{json.loads(create_response)['statusText']}")

    running_cycles[user_id] = True
    threading.Thread(target=run_cycle, args=(user_id,)).start()

def kill_cycle(update: Update, context: CallbackContext):
    user_id = str(update.message.chat_id)
    if not running_cycles.get(user_id, False):
        update.message.reply_text("⚠️ No active cycle to stop.")
        return

    update.message.reply_text("🛑 Stopping cycle...")
    running_cycles[user_id] = False

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(), bot)
    dispatcher.process_update(update)
    return "OK", 200

def set_webhook():
    webhook_url = f"{RAILWAY_URL}/{TOKEN}"
    bot.setWebhook(webhook_url)
    print(f"Webhook set to {webhook_url}")

def main():
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("setver", set_verification))
    dispatcher.add_handler(CommandHandler("chkver", chk_verification))
    dispatcher.add_handler(CommandHandler("run", process_cycle))
    dispatcher.add_handler(CommandHandler("kill", kill_cycle))

    set_webhook()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

if __name__ == "__main__":
    main()
