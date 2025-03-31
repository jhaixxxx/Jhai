import requests
import time
import threading
import json
import os
import asyncio
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, CallbackContext

# Telegram Bot Token
TOKEN = "7881208281:AAHVDGWvw5vhMo3FeYkitHnzZ8trEZd1nfE"

# Telegram Chat ID (for updates)
CHAT_ID = None  # Set this to None so all users can use the bot

# Base URL for API Requests
BASE_URL = "https://boats-app-cba6ae7713ab.herokuapp.com"

# Default verification codes (Configurable via Telegram)
verification_codes = {
    "create": "default_create_code",
    "cycle": "default_cycle_code",
    "end": "default_end_code"
}

# Bot instance
bot = Bot(token=TOKEN)

# Flask app for webhook
app = Flask(__name__)

# Running flag
running = False


async def send_request(name, url, data=None, method="POST"):
    """Helper function to send HTTP requests."""
    await bot.send_message(chat_id=CHAT_ID, text=f"🔄 Sending {name} request...")

    if method == "POST":
        response = requests.post(url, json=data)
    else:
        response = requests.get(url)

    try:
        response_json = response.json()
        formatted_response = json.dumps(response_json, indent=4)
    except json.JSONDecodeError:
        formatted_response = response.text

    await bot.send_message(chat_id=CHAT_ID, text=f"✔ {name} Response:\n{formatted_response}")


async def countdown(seconds, message):
    """Countdown timer with Telegram notifications."""
    while seconds > 0 and running:
        await bot.send_message(chat_id=CHAT_ID, text=f"⏳ {message} in {seconds}s...")
        await asyncio.sleep(10)
        seconds -= 10
    await bot.send_message(chat_id=CHAT_ID, text="✅ Continuing...")


async def process_loop():
    """Main process loop."""
    global running
    counter = 1

    while running:
        await bot.send_message(chat_id=CHAT_ID, text=f"🔄 Cycle {counter} Starting...")

        await send_request("Create New Session", f"{BASE_URL}/createNewSession", {"verificationCode": verification_codes["create"]})
        await countdown(60, "Waiting after Create Session")

        await send_request("Get Cycle Ads Reward", f"{BASE_URL}/getCycleAdsReward", {"verificationCode": verification_codes["cycle"]})
        await countdown(30, "Waiting after Get Cycle Ads Reward")

        await send_request("End Session", f"{BASE_URL}/endActiveSession", method="GET")

        counter += 1


async def start(update: Update, context: CallbackContext):
    """Start the process loop."""
    global running
    if not running:
        running = True
        asyncio.create_task(process_loop())
        await update.message.reply_text("✅ Bot Started!")
    else:
        await update.message.reply_text("⚠️ Already Running!")


async def stop(update: Update, context: CallbackContext):
    """Stop the process loop."""
    global running
    running = False
    await update.message.reply_text("🛑 Bot Stopped!")


async def set_verification(update: Update, context: CallbackContext):
    """Set verification codes."""
    if len(context.args) < 2:
        await update.message.reply_text("⚠️ Usage: /setver <create|cycle|end> <code>")
        return

    key, value = context.args[0], context.args[1]
    if key in verification_codes:
        verification_codes[key] = value
        await update.message.reply_text(f"✅ Updated {key} verification code!")
    else:
        await update.message.reply_text("⚠️ Invalid key! Use: create, cycle, or end.")


async def chkver(update: Update, context: CallbackContext):
    """Check verification codes."""
    ver_info = "\n".join([f"{key}: {value}" for key, value in verification_codes.items()])
    await update.message.reply_text(f"🔍 Current Verification Codes:\n{ver_info}")


def run_flask():
    """Run Flask app to listen for webhook requests."""
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


def main():
    """Main function to start the Telegram bot."""
    global CHAT_ID

    # Create Telegram application
    app = Application.builder().token(TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("setver", set_verification))
    app.add_handler(CommandHandler("chkver", chkver))

    # Start Flask server in a separate thread
    threading.Thread(target=run_flask, daemon=True).start()

    # Start polling for Telegram commands
    app.run_polling()


if __name__ == "__main__":
    main()
