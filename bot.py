import time
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, CallbackContext

TOKEN = "7881208281:AAFcr2FB-9xThO9VeGAAN0loaVgVTm_g72k"
WEBHOOK_URL = "https://jhai-2.onrender.com"

bot = Bot(TOKEN)
app = Flask(__name__)

verification_codes = {
    "createNewSession": "5a52eb89e0208ead2c23809a536a876a...",
    "getCycleAdsReward1": "5a52eb89e0208ead2c23809a536a876a...",
    "getCycleAdsReward2": "5a52eb89e0208ead2c23809a536a876a...",
    "saveFocusedTime1": "809eb7d6fe2807820ddc754ccafb1e5d...",
    "getCycleAdsReward3": "5a52eb89e0208ead2c23809a536a876a...",
    "saveFocusedTime2": "809eb7d6fe2807820ddc754ccafb1e5d...",
    "endActiveSession": "5a52eb89e0208ead2c23809a536a876a..."
}

def send_request(endpoint, verification_code, chat_id):
    url = f"https://boats-app-cba6ae7713ab.herokuapp.com{endpoint}"
    headers = {"Content-Type": "application/json"}
    data = {"verificationCode": verification_code}
    response = requests.post(url, json=data, headers=headers)
    bot.send_message(chat_id, f"✅ {endpoint} | Status: {response.status_code}\n{response.text}")

async def start_session(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    await update.message.reply_text("🚀 Starting session...")

    send_request("/createNewSession", verification_codes["createNewSession"], chat_id)
    time.sleep(60)
    send_request("/getCycleAdsReward", verification_codes["getCycleAdsReward1"], chat_id)
    time.sleep(60)
    send_request("/getCycleAdsReward", verification_codes["getCycleAdsReward2"], chat_id)
    time.sleep(60)
    send_request("/saveFocusedTime", verification_codes["saveFocusedTime1"], chat_id)
    time.sleep(60)
    send_request("/getCycleAdsReward", verification_codes["getCycleAdsReward3"], chat_id)
    send_request("/saveFocusedTime", verification_codes["saveFocusedTime2"], chat_id)
    send_request("/endActiveSession", verification_codes["endActiveSession"], chat_id)
    
    await update.message.reply_text("✅ Session completed!")

@app.route(f"/{TOKEN}", methods=["POST"])
def receive_update():
    update = Update.de_json(request.get_json(), bot)
    application.process_update(update)
    return "OK", 200

def main():
    global application
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start_session", start_session))
    
    bot.set_webhook(WEBHOOK_URL + "/" + TOKEN)
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    main()
