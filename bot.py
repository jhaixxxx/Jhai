import requests
import time
import threading
import json
import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, CallbackContext

# Telegram Bot Token
TOKEN = "7118239951:AAHN8AkMRvscPXFDmHRLVcDyL8o-5yJJuBY"
CHAT_ID = "6735321947"

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

# Flask app for webhook support
app = Flask(__name__)

# Running flag
running = False

def send_request(name, url, data=None, method="POST"):
    """Helper function to send HTTP requests and notify Telegram."""
    bot.send_message(chat_id=CHAT_ID, text=f"🔄 Sending {name} request...")

    try:
        if method == "POST":
            response = requests.post(url, json=data)
        else:
            response = requests.get(url)

        response_json = response.json()
        formatted_response = json.dumps(response_json, indent=4)

    except requests.RequestException as e:
        formatted_response = f"⚠️ Error: {e}"
    except json.JSONDecodeError:
        formatted_response = response.text

    bot.send_message(chat_id=CHAT_ID, text=f"✔ {name} Response:\n{formatted_response}")

def countdown(seconds, message):
    """Countdown timer with Telegram updates."""
    while seconds > 0 and running:
        bot.send_message(chat_id=CHAT_ID, text=f"⏳ {message} in {seconds}s...")
        time.sleep(10)
        seconds -= 10
    bot.send_message(chat_id=CHAT_ID, text="✅ Continuing...")

def process_loop():
    """Main process loop with regular updates."""
    global running
    counter = 1

    while running:
        bot.send_message(chat_id=CHAT_ID, text=f"🔁 Cycle {counter} Starting...")

        send_request("Create New Session", f"{BASE_URL}/createNewSession", {"verificationCode": verification_codes["create"]})
        countdown(60, "Waiting after Create Session")

        send_request("Get Cycle Ads Reward", f"{BASE_URL}/getCycleAdsReward", {"verificationCode": verification_codes["cycle"]})
        countdown(30, "Waiting after Get Cycle Ads Reward")

        send_request("End Session", f"{BASE_URL}/endActiveSession", method="GET")

        bot.send_message(chat_id=CHAT_ID, text=f"✅ Cycle {counter} Completed Successfully!\n🕐 Next cycle in 10s...")
        time.sleep(10)  # Short delay before restarting the next cycle
        
        counter += 1

async def start(update: Update, context: CallbackContext):
    """Start the process loop and send an update."""
    global running
    if not running:
        running = True
        bot.send_message(chat_id=CHAT_ID, text="🚀 Bot is now running!")
        threading.Thread(target=process_loop).start()
        await update.message.reply_text("✅ Bot Started!")
    else:
        await update.message.reply_text("⚠️ Already Running!")

async def stop(update: Update, context: CallbackContext):
    """Stop the process loop and send an update."""
    global running
    running = False
    bot.send_message(chat_id=CHAT_ID, text="🛑 Bot has been stopped.")
    await update.message.reply_text("🛑 Bot Stopped!")

async def set_verification(update: Update, context: CallbackContext):
    """Set verification codes and send confirmation."""
    if len(context.args) < 2:
        await update.message.reply_text("⚠️ Usage: /setver <create|cycle|end> <code>")
        return

    key, value = context.args[0], context.args[1]
    if key in verification_codes:
        verification_codes[key] = value
        await update.message.reply_text(f"✅ Updated {key} verification code!")
    else:
        await update.message.reply_text("⚠️ Invalid key! Use: create, cycle, or end.")

async def check_verification(update: Update, context: CallbackContext):
    """Check the current verification codes."""
    config_text = (
        "🔎 *Current Verification Codes:*\n"
        f"📌 *Create:* `{verification_codes['create']}`\n"
        f"📌 *Cycle:* `{verification_codes['cycle']}`\n"
        f"📌 *End:* `{verification_codes['end']}`"
    )
    await update.message.reply_text(config_text, parse_mode="Markdown")

def main():
    """Main function to start the Telegram bot."""
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("setver", set_verification))
    app.add_handler(CommandHandler("chkver", check_verification))  # New command added

    app.run_polling()

if __name__ == "__main__":
    main()
