import time
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext

TOKEN = "7881208281:AAFcr2FB-9xThO9VeGAAN0loaVgVTm_g72k"
WEBHOOK_URL = "https://jhai-2.onrender.com"

bot = Bot(TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, None, workers=4, use_context=True)

verification_codes = {
    "createNewSession": "5a52eb89e0208ead2c23809a536a876a5c06d3e446d4fa13466afac52b1fd026cba3b08ad5796791021c91b120cedc2bd824a10736cf4973effb50f24d4500b1",
    "getCycleAdsReward1": "5a52eb89e0208ead2c23809a536a876a5c06d3e446d4fa13466afac52b1fd026cba3b08ad5796791021c91b120cedc2b5f3bd2b6eebb732ea7b4ef9f1405cc0d",
    "getCycleAdsReward2": "5a52eb89e0208ead2c23809a536a876a5c06d3e446d4fa13466afac52b1fd026cba3b08ad5796791021c91b120cedc2b5c69aec1e5957cee8d3f11a89779f3f1",
    "saveFocusedTime1": "809eb7d6fe2807820ddc754ccafb1e5d23e2d1e8a8487279adf6f2050e855ec9f33e0c5efff08083ae0775bea3c3c0262b6de9a5ccdcceec10a8729f930edcd75",
    "getCycleAdsReward3": "5a52eb89e0208ead2c23809a536a876a5c06d3e446d4fa13466afac52b1fd026cba3b08ad5796791021c91b120cedc2b6744aaea409ba1d75bfb3565add734a6",
    "saveFocusedTime2": "809eb7d6fe2807820ddc754ccafb1e5d66cee7aac204422136b85a8574afdbb3f33e0c5efff08083ae0775bea3c3c0262b6de9a5ccdcceec10a8729f930edcd74",
    "endActiveSession": "5a52eb89e0208ead2c23809a536a876a5c06d3e446d4fa13466afac52b1fd026cba3b08ad5796791021c91b120cedc2b26b6df8a287534765006656204ff31e0"
}

def send_request(endpoint, verification_code, chat_id):
    url = f"https://boats-app-cba6ae7713ab.herokuapp.com{endpoint}"
    headers = {"Content-Type": "application/json"}
    data = {"verificationCode": verification_code}
    response = requests.post(url, json=data, headers=headers)
    bot.send_message(chat_id, f"✅ {endpoint} | Status: {response.status_code}\n{response.text}")

def start_session(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    bot.send_message(chat_id, "🚀 Starting session...")

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
    bot.send_message(chat_id, "✅ Session completed!")

def webhook(update: Update, context: CallbackContext):
    dispatcher.process_update(update)

@app.route(f"/{TOKEN}", methods=["POST"])
def receive_update():
    update = Update.de_json(request.get_json(), bot)
    webhook(update, None)
    return "OK", 200

def main():
    bot.set_webhook(WEBHOOK_URL + "/" + TOKEN)
    dispatcher.add_handler(CommandHandler("start_session", start_session))
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    main()
