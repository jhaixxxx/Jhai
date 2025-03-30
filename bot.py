import json
import time
import random
import string
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext

# Bot Configuration
TOKEN = "7118239951:AAHN8AkMRvscPXFDmHRLVcDyL8o-5yJJuBY"
ADMIN_ID = 6735321947
KEY_FILE = "keys.json"
DOMAIN = "https://www.uujl.com"

def load_keys():
    try:
        with open(KEY_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_keys(keys):
    with open(KEY_FILE, "w") as file:
        json.dump(keys, file, indent=4)

def generate_key(update: Update, context: CallbackContext):
    if update.message.chat_id != ADMIN_ID:
        update.message.reply_text("You are not authorized to generate keys.")
        return
    
    key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    keys = load_keys()
    keys[key] = time.time() + 86400  # 24-hour expiration
    save_keys(keys)
    
    update.message.reply_text(f"Generated Key: `{key}` (Expires in 24h)", parse_mode="Markdown")

def activate_key(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Usage: /activate <KEY>")
        return
    
    key = context.args[0]
    keys = load_keys()
    
    if key in keys and keys[key] > time.time():
        context.user_data["premium"] = True
        del keys[key]
        save_keys(keys)
        update.message.reply_text("✅ Premium Activated!")
    else:
        update.message.reply_text("❌ Invalid or Expired Key!")

def check_status(update: Update, context: CallbackContext):
    if context.user_data.get("premium", False):
        update.message.reply_text("✅ You are a Premium User!")
    else:
        update.message.reply_text("❌ You are NOT a Premium User!")

def setup_selenium():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    service = Service("chromedriver")
    return webdriver.Chrome(service=service, options=options)

def auto_register(update: Update, context: CallbackContext):
    if not context.user_data.get("premium", False):
        update.message.reply_text("❌ You need a Premium Account to use this feature.")
        return
    
    driver = setup_selenium()
    driver.get(f"{DOMAIN}/m/register")
    
    username = "User" + str(random.randint(100000, 999999))
    password = "Paidsc123"
    
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "confimpsw").send_keys(password)
    driver.find_element(By.CLASS_NAME, "submit-btn").click()
    
    time.sleep(2)
    driver.quit()
    
    update.message.reply_text(f"✅ Registered!\nUsername: `{username}`\nPassword: `{password}`", parse_mode="Markdown")

def bind_bank(update: Update, context: CallbackContext):
    if not context.user_data.get("premium", False):
        update.message.reply_text("❌ You need a Premium Account to use this feature.")
        return
    
    driver = setup_selenium()
    driver.get(f"{DOMAIN}/m/securityCenter/addBankCardPix")
    
    driver.find_element(By.NAME, "payee").send_keys("***** ******")
    driver.find_element(By.NAME, "customField").send_keys("09" + str(random.randint(100000000, 999999999)))
    driver.find_element(By.NAME, "withdraw").send_keys("000000")
    driver.find_element(By.NAME, "withdrawT").send_keys("000000")
    driver.find_element(By.CLASS_NAME, "btn-success").click()
    
    time.sleep(2)
    driver.quit()
    
    update.message.reply_text("✅ Bank Successfully Bound!")

def claim_egg(update: Update, context: CallbackContext):
    if not context.user_data.get("premium", False):
        update.message.reply_text("❌ You need a Premium Account to use this feature.")
        return
    
    driver = setup_selenium()
    driver.get(f"{DOMAIN}/m/home")
    
    try:
        claim_button = driver.find_element(By.CLASS_NAME, "item-claim")
        claim_button.click()
        time.sleep(2)
    except:
        update.message.reply_text("⚠️ 'Claim' button not found!")
    
    try:
        smash_button = driver.find_element(By.CLASS_NAME, "prize_message")
        smash_button.click()
        time.sleep(2)
        update.message.reply_text("🔨 Egg Smashed Successfully!")
    except:
        update.message.reply_text("⚠️ 'Smash Egg' button not found!")
    
    driver.quit()

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("generate_key", generate_key))
    dp.add_handler(CommandHandler("activate", activate_key, pass_args=True))
    dp.add_handler(CommandHandler("status", check_status))
    dp.add_handler(CommandHandler("register", auto_register))
    dp.add_handler(CommandHandler("bind_bank", bind_bank))
    dp.add_handler(CommandHandler("claim_egg", claim_egg))
    
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
