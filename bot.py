import requests
import time
import threading
import json
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, CallbackContext

# Telegram Bot Token
TOKEN = "7881208281:AAFmFi1JgrGPx6jgVB1yPA4E_oWNrK3WZi8"

# Base URL for API Requests
BASE_URL = "https://boats-app-cba6ae7713ab.herokuapp.com"

# Default verification codes (Configurable via Telegram)
verification_codes = {
    "create": "default_create_code",
    "cycle": "default_cycle_code",
    "end": "default_end_code"
}

# Running flag
running = False


async def send_update(context: CallbackContext, message: str):
    """Send updates to all users who interact with the bot."""
    for user_id in context.bot_data.get("users", set()):
        await context.bot.send_message(chat_id=user_id, text=message)


def send_request(name, url, data=None, method="POST"):
    """Helper function to send HTTP requests and return response."""
    print(f"🔄 Sending {name} request...")

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

    print(f"✔ {name} Response:\n{formatted_response}")
    return formatted_response


def countdown(seconds, message, context: CallbackContext):
    """Countdown timer with real-time Telegram updates."""
    while seconds > 0 and running:
        context.application.create_task(send_update(context, f"⏳ {message} in {seconds}s..."))
        time.sleep(10)
        seconds -= 10
    context.application.create_task(send_update(context, "✅ Continuing..."))


def process_loop(context: CallbackContext):
    """Main process loop with live updates."""
    global running
    counter = 1

    while running:
        context.application.create_task(send_update(context, f"🔄 Cycle {counter} Starting..."))

        response = send_request("Create New Session", f"{BASE_URL}/createNewSession", {"verificationCode": verification_codes["create"]})
        context.application.create_task(send_update(context, f"✅ Create Session Response:\n{response}"))
        countdown(60, "Waiting after Create Session", context)

        response = send_request("Get Cycle Ads Reward", f"{BASE_URL}/getCycleAdsReward", {"verificationCode": verification_codes["cycle"]})
        context.application.create_task(send_update(context, f"✅ Cycle Ads Reward Response:\n{response}"))
        countdown(30, "Waiting after Get Cycle Ads Reward", context)

        response = send_request("End Session", f"{BASE_URL}/endActiveSession", method="GET")
        context.application.create_task(send_update(context, f"✅ End Session Response:\n{response}"))

        context.application.create_task(send_update(context, f"✅ Cycle {counter} Completed!\n🕐 Next cycle in 10s..."))
        time.sleep(10)

        counter += 1


async def start(update: Update, context: CallbackContext):
    """Start the process loop and register user for updates."""
    global running
    user_id = update.message.chat_id
    context.bot_data.setdefault("users", set()).add(user_id)

    if not running:
        running = True
        await update.message.reply_text("🚀 Bot is now running!")
        threading.Thread(target=process_loop, args=(context,)).start()
    else:
        await update.message.reply_text("⚠️ Already Running!")


async def stop(update: Update, context: CallbackContext):
    """Stop the process loop and notify users."""
    global running
    running = False
    await update.message.reply_text("🛑 Bot Stopped!")


async def set_verification(update: Update, context: CallbackContext):
    """Set verification codes dynamically."""
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
    """Main function to start the bot."""
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("setver", set_verification))
    app.add_handler(CommandHandler("chkver", check_verification))

    print("✅ Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
