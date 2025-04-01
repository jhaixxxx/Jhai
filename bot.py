import requests
import random
import json
import time
import threading
import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, CallbackContext

# ---------------------- CONFIGURATION ----------------------

TOKEN = "7881208281:AAGR8DAaGV2s2AvyquL95h90ZMVPB11Q8RM"  # Replace with your bot token
BASE_URL = "https://boats-app-cba6ae7713ab.herokuapp.com"

DATA_FILE = "users.json"
ALLOWED_USERS = ["6735321947", "2120592843"]  # Replace with allowed Telegram user IDs

# Initialize Flask app (for Railway compatibility)
flask_app = Flask(__name__)

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
        return response.json()
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response"}

async def start(update: Update, context: CallbackContext):
    """Start the bot."""
    await update.message.reply_text("✅ Welcome! Use /setver to set your verification codes.")

async def set_verification(update: Update, context: CallbackContext):
    """Set user-specific verification codes (restricted access)."""
    user_id = str(update.message.chat_id)

    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("❌ You are not authorized to use this command.\nContact: @urJOSH911")
        return

    if len(context.args) < 2:
        await update.message.reply_text("⚠️ Usage: /setver <create|cycle|end|auth|status> <code>")
        return

    key, value = context.args[0], context.args[1]

    if key not in ["create", "cycle", "end", "auth", "status"]:
        await update.message.reply_text("⚠️ Invalid key! Use: create, cycle, end, status, or auth.")
        return

    if user_id not in users:
        users[user_id] = {}

    users[user_id][key] = value
    save_users(users)

    await update.message.reply_text(f"✅ Updated {key} verification code!")

async def chk_verification(update: Update, context: CallbackContext):
    """Check saved verification codes for the user."""
    user_id = str(update.message.chat_id)

    if user_id not in users:
        await update.message.reply_text("⚠️ No verification codes or auth set. Use /setver to add.")
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

    await update.message.reply_text(message)

async def process_cycle(update: Update, context: CallbackContext):
    """Start the cycle for the user."""
    user_id = str(update.message.chat_id)

    if user_id not in users or any(key not in users[user_id] for key in ["create", "cycle", "end", "auth", "status"]):
        await update.message.reply_text("⚠️ Set verification codes first using /setver")
        return

    if user_id in running_cycles and running_cycles[user_id]:
        await update.message.reply_text("⚠️ A cycle is already running!")
        return

    await update.message.reply_text("🔄 Starting process...")

    # Step 1: Create New Session
    create_url = f"{BASE_URL}/createNewSession"
    create_data = {"verificationCode": users[user_id]["create"]}
    create_response = send_request("Create New Session", create_url, create_data)

    await update.message.reply_text(f"✔ Create New Session Response:\n{create_response.get('statusText', 'Error')}")

    # Start looping for Cycle Reward
    running_cycles[user_id] = True
    threading.Thread(target=run_cycle, args=(user_id,)).start()

async def kill_cycle(update: Update, context: CallbackContext):
    """Stop the cycle and end session."""
    user_id = str(update.message.chat_id)

    if user_id not in running_cycles or not running_cycles[user_id]:
        await update.message.reply_text("⚠️ No active cycle to stop.")
        return

    await update.message.reply_text("🛑 Stopping cycle...")

    running_cycles[user_id] = False

    # Step 3: End Session
    end_url = f"{BASE_URL}/endActiveSession"
    end_data = {"verificationCode": users[user_id]["end"]}
    end_response = send_request("End Session", end_url, end_data)

    await update.message.reply_text(f"✔ End Session Response:\n{end_response.get('statusText', 'Error')}")

    await update.message.reply_text("✅ Cycle stopped successfully!")

# ---------------------- TELEGRAM BOT INITIALIZATION ----------------------

telegram_app = Application.builder().token(TOKEN).build()

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("setver", set_verification))
telegram_app.add_handler(CommandHandler("chkver", chk_verification))
telegram_app.add_handler(CommandHandler("run", process_cycle))
telegram_app.add_handler(CommandHandler("kill", kill_cycle))

# ---------------------- RUN SCRIPT ----------------------

def run_telegram_bot():
    """Run the Telegram bot."""
    telegram_app.run_polling()

if __name__ == "__main__":
    # Start Telegram bot in a separate thread
    threading.Thread(target=run_telegram_bot).start()

    # Start Flask app for Railway deployment
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
