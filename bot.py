import time import requests from telegram import Update, Bot from telegram.ext import Updater, CommandHandler, CallbackContext

def send_request(endpoint, verification_code, update): url = f"https://boats-app-cba6ae7713ab.herokuapp.com{endpoint}" headers = { "currency": "USD", "Connection": "close", "rentappsetup": "true", "version": "2.7", "language": "English", "packageName": "com.boat.app.adventure", "versionCode": "27", "storeType": "google_play", "authcode": ":v44pk8:g9>", "Content-Type": "application/json; charset=utf-8", "Accept-Encoding": "gzip", "User-Agent": "okhttp/5.0.0-alpha.14" } data = {"verificationCode": verification_code} response = requests.post(url, json=data, headers=headers) result = response.json() update.message.reply_text(f"✅ Request to {endpoint} | Status: {response.status_code}\nResponse: {result}") return result

verification_codes = { "createNewSession": "5a52eb89e0208ead2c23809a536a876a5c06d3e446d4fa13466afac52b1fd026cba3b08ad5796791021c91b120cedc2bd824a10736cf4973effb50f24d4500b1", "getCycleAdsReward1": "5a52eb89e0208ead2c23809a536a876a5c06d3e446d4fa13466afac52b1fd026cba3b08ad5796791021c91b120cedc2b5f3bd2b6eebb732ea7b4ef9f1405cc0d", "getCycleAdsReward2": "5a52eb89e0208ead2c23809a536a876a5c06d3e446d4fa13466afac52b1fd026cba3b08ad5796791021c91b120cedc2b5c69aec1e5957cee8d3f11a89779f3f1", "saveFocusedTime1": "809eb7d6fe2807820ddc754ccafb1e5d23e2d1e8a8487279adf6f2050e855ec9f33e0c5efff08083ae0775bea3c3c0262b6de9a5ccdcceec10a8729f930edcd75", "getCycleAdsReward3": "5a52eb89e0208ead2c23809a536a876a5c06d3e446d4fa13466afac52b1fd026cba3b08ad5796791021c91b120cedc2b6744aaea409ba1d75bfb3565add734a6", "saveFocusedTime2": "809eb7d6fe2807820ddc754ccafb1e5d66cee7aac204422136b85a8574afdbb3f33e0c5efff08083ae0775bea3c3c0262b6de9a5ccdcceec10a8729f930edcd74", "endActiveSession": "5a52eb89e0208ead2c23809a536a876a5c06d3e446d4fa13466afac52b1fd026cba3b08ad5796791021c91b120cedc2b26b6df8a287534765006656204ff31e0" }

def start_session(update: Update, context: CallbackContext): update.message.reply_text("🚀 Starting session...") send_request("/createNewSession", verification_codes["createNewSession"], update) time.sleep(60)

send_request("/getCycleAdsReward", verification_codes["getCycleAdsReward1"], update)
time.sleep(60)
send_request("/getCycleAdsReward", verification_codes["getCycleAdsReward2"], update)
time.sleep(60)

send_request("/saveFocusedTime", verification_codes["saveFocusedTime1"], update)
time.sleep(60)

send_request("/getCycleAdsReward", verification_codes["getCycleAdsReward3"], update)
send_request("/saveFocusedTime", verification_codes["saveFocusedTime2"], update)
send_request("/endActiveSession", verification_codes["endActiveSession"], update)

update.message.reply_text("✅ Session completed successfully!")

def main(): bot_token = "7881208281:AAE9CQmWBtL5g9U6gioor2jzttqzM3w6fAU" updater = Updater(bot_token, use_context=True) dp = updater.dispatcher

dp.add_handler(CommandHandler("start_session", start_session))

updater.start_polling()
updater.idle()

if name == "main": main()

