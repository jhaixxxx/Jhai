import requests
import json
import time
import threading
import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext

# ---------------------- CONFIGURATION ----------------------

TOKEN = "7881208281:AAEFwl96PGwKcO2sSuSPES8yAZ4SxC6OrrA"  # Replace with your bot token
BASE_URL = "https://boats-app-cba6ae7713ab.herokuapp.com"

DATA_FILE = "users.json"
ALLOWED_USERS = ["6735321947", "2120592843"]  # Replace with allowed Telegram user IDs

# Initialize Flask app (needed for Pydroid)
app = Flask(__name__)

# ---------------------- LOAD & SAVE USER DATA ----------------------

def load_users():
    """Load user data from JSON file."""
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    """Save user data to JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=4)

users = load_users()

# ---------------------- TELEGRAM BOT FUNCTIONS ----------------------

bot = Bot(token=TOKEN)
running_cycles = {}

def send_request(name, url, data=None, method="POST"):
    """Send API request and notify user."""
    session = requests.Session()

    if method == "POST":
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
        response = session.post(url, headers=headers, json=data)
    else:
        response = session.get(url)

    try:
        response_json = response.json()
        return json.dumps(response_json, indent=4)
    except json.JSONDecodeError:
        return response.text

def start(update: Update, context: CallbackContext):
    """Start the bot."""
    update.message.reply_text("✅ Welcome! Use /setver to set your verification codes.")

def set_verification(update: Update, context: CallbackContext):
    """Set user-specific verification codes (restricted access)."""
    user_id = str(update.message.chat_id)

    if user_id not in ALLOWED_USERS:
        update.message.reply_text("❌ You are not authorized to use this command.\nContact : @urJOSH911")
        return

    if len(context.args) < 2:
        update.message.reply_text("⚠️ Usage: /setver <create|cycle|end|auth> <code>")
        return

    key, value = context.args[0], context.args[1]

    if key not in ["create", "cycle", "end", "auth"]:
        update.message.reply_text("⚠️ Invalid key! Use: create, cycle, end, or auth.")
        return

    if user_id not in users:
        users[user_id] = {}

    users[user_id][key] = value
    save_users(users)

    update.message.reply_text(f"✅ Updated {key} verification code!")

def chk_verification(update: Update, context: CallbackContext):
    """Check saved verification codes for the user."""
    user_id = str(update.message.chat_id)

    if user_id not in users:
        update.message.reply_text("⚠️ No verification codes set. Use /setver to add.")
        return

    codes = users[user_id]
    message = (
        f"✅ AUTH: {codes.get('auth', 'Not Set')}\n"
        f"✅ Your verification codes:\n"
        f"🔹 Create: {codes.get('create', 'Not Set')}\n"
        f"🔹 Cycle: {codes.get('cycle', 'Not Set')}\n"
        f"🔹 End: {codes.get('end', 'Not Set')}"
    )

    update.message.reply_text(message)

def run_cycle(user_id):
    """Loop the cycle request every 30-60 seconds."""
    while running_cycles.get(user_id, False):
        reward_url = f"{BASE_URL}/getCycleAdsReward"
        reward_data = {"verificationCode": users[user_id]["cycle"]}
        reward_response = send_request("Get Cycle Ads Reward", reward_url, reward_data)

        bot.send_message(chat_id=user_id, text=f"✔ Get Cycle Ads Reward Response:\n{reward_response}")
        time.sleep(30 + (time.time() % 30))  # Random 30-60s delay

    bot.send_message(chat_id=user_id, text="🛑 Cycle stopped.")

def process_cycle(update: Update, context: CallbackContext):
    """Start the cycle for the user."""
    user_id = str(update.message.chat_id)

    if user_id not in users or "create" not in users[user_id] or "cycle" not in users[user_id] or "end" not in users[user_id]:
        update.message.reply_text("⚠️ Set verification codes first using /setver")
        return

    if user_id in running_cycles and running_cycles[user_id]:
        update.message.reply_text("⚠️ A cycle is already running!")
        return

    update.message.reply_text("🔄 Starting process...")

    # Step 1: Create New Session
    create_url = f"{BASE_URL}/createNewSession"
    create_data = {"verificationCode": users[user_id]["create"]}
    create_response = send_request("Create New Session", create_url, create_data)
    bot.send_message(chat_id=user_id, text=f"✔ Create New Session Response:\n{create_response}")

    # Start looping for Cycle Reward
    running_cycles[user_id] = True
    thread = threading.Thread(target=run_cycle, args=(user_id,))
    thread.start()

def kill_cycle(update: Update, context: CallbackContext):
    """Stop the cycle and end session."""
    user_id = str(update.message.chat_id)

    if user_id not in running_cycles or not running_cycles[user_id]:
        update.message.reply_text("⚠️ No active cycle to stop.")
        return

    update.message.reply_text("🛑 Stopping cycle...")

    running_cycles[user_id] = False

    # Step 3: End Session
    end_url = f"{BASE_URL}/endActiveSession"
    end_data = {"verificationCode": users[user_id]["end"]}
    end_response = send_request("End Session", end_url, end_data)
    bot.send_message(chat_id=user_id, text=f"✔ End Session Response:\n{end_response}")

    update.message.reply_text("✅ Cycle stopped successfully!")

# ---------------------- TELEGRAM BOT INITIALIZATION ----------------------

def main():
    """Start the bot."""
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("setver", set_verification))
    dp.add_handler(CommandHandler("chkver", chk_verification))
    dp.add_handler(CommandHandler("run", process_cycle))
    dp.add_handler(CommandHandler("kill", kill_cycle))

    updater.start_polling()
    updater.idle()

# ---------------------- FLASK ROUTE FOR WEBHOOK ----------------------

@app.route('/jhai/bot.py', methods=['POST'])
def telegram_webhook():
    """Handle the incoming webhook request from Telegram."""
    json_str = request.get_data().decode('UTF-8')
    update = Update.de_json(json.loads(json_str), bot)
    # Process the update here, handling the incoming message
    updater.dispatcher.process_update(update)
    return 'OK', 200

# ---------------------- RUN SCRIPT ----------------------

if __name__ == "__main__":
    threading.Thread(target=main).start()
    app.run(host="0.0.0.0", port=5000)
