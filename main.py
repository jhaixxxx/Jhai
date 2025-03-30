import json import time import random from datetime import datetime, timedelta from telegram import Update, Bot from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext from selenium import webdriver from selenium.webdriver.common.by import By

Load or create key storage

def load_keys(): try: with open("key.json", "r") as file: return json.load(file) except FileNotFoundError: return {}

def save_keys(keys): with open("key.json", "w") as file: json.dump(keys, file, indent=4)

keys = load_keys() ADMIN_ID = 6735321947  # Replace with your Telegram ID TOKEN = "7118239951:AAHN8AkMRvscPXFDmHRLVcDyL8o-5yJJuBY"

Generate new key

def generate_key(update: Update, context: CallbackContext): if update.message.chat_id != ADMIN_ID: update.message.reply_text("Unauthorized!") return

key = str(random.randint(100000, 999999))
expiry = (datetime.now() + timedelta(days=7)).isoformat()
keys[key] = {"expires": expiry}
save_keys(keys)
update.message.reply_text(f"Generated Key: {key} (Expires in 7 days)")

Validate key

def activate_premium(update: Update, context: CallbackContext): if len(context.args) != 1: update.message.reply_text("Usage: /activate <key>") return

key = context.args[0]
if key in keys:
    expiry = datetime.fromisoformat(keys[key]["expires"])
    if datetime.now() < expiry:
        update.message.reply_text("Premium activated!")
    else:
        update.message.reply_text("Key expired!")
else:
    update.message.reply_text("Invalid key!")

Auto-delete expired keys

def cleanup_keys(): global keys keys = {k: v for k, v in keys.items() if datetime.fromisoformat(v["expires"]) > datetime.now()} save_keys(keys)

def get_random_username(): return 'User' + str(random.randint(100000, 999999))

def get_random_phone_number(): return '09' + str(random.randint(100000000, 999999999))

def register_account(update: Update, context: CallbackContext): options = webdriver.ChromeOptions() options.add_argument("--headless") driver = webdriver.Chrome(options=options)

try:
    driver.get("https://www.uujl.com/m/register")
    username = get_random_username()
    password = "Paidsc123"
    
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "confimpsw").send_keys(password)
    driver.find_element(By.CLASS_NAME, "submit-btn").click()
    
    time.sleep(2)
    update.message.reply_text(f"Account Registered:\nUsername: {username}\nPassword: {password}")
except Exception as e:
    update.message.reply_text(f"Error: {str(e)}")
finally:
    driver.quit()

def bind_bank(update: Update, context: CallbackContext): options = webdriver.ChromeOptions() options.add_argument("--headless") driver = webdriver.Chrome(options=options)

try:
    driver.get("https://www.uujl.com/m/securityCenter/addBankCardPix")
    
    driver.find_element(By.NAME, "payee").send_keys("***** ******")
    driver.find_element(By.NAME, "customField").send_keys(get_random_phone_number())
    driver.find_element(By.NAME, "withdraw").send_keys("000000")
    driver.find_element(By.NAME, "withdrawT").send_keys("000000")
    
    driver.find_element(By.CLASS_NAME, "btn-success").click()
    
    time.sleep(2)
    update.message.reply_text("Bank successfully bound!")
except Exception as e:
    update.message.reply_text(f"Error: {str(e)}")
finally:
    driver.quit()

def claim_egg(update: Update, context: CallbackContext): options = webdriver.ChromeOptions() options.add_argument("--headless") driver = webdriver.Chrome(options=options)

try:
    driver.get("https://www.uujl.com/m/home")
    time.sleep(2)
    
    claim_button = driver.find_element(By.CLASS_NAME, "item-claim")
    claim_button.click()
    time.sleep(2)
    
    smash_button = driver.find_element(By.CLASS_NAME, "prize_message")
    if smash_button:
        smash_button.click()
        time.sleep(3)
        update.message.reply_text("Egg smashed successfully!")
    else:
        update.message.reply_text("No smash egg button found, skipping.")
except Exception as e:
    update.message.reply_text(f"Error: {str(e)}")
finally:
    driver.quit()

def main(): cleanup_keys() bot = Bot(TOKEN) updater = Updater(TOKEN, use_context=True) dp = updater.dispatcher

dp.add_handler(CommandHandler("generate_key", generate_key))
dp.add_handler(CommandHandler("activate", activate_premium))
dp.add_handler(CommandHandler("register", register_account))
dp.add_handler(CommandHandler("bindbank", bind_bank))
dp.add_handler(CommandHandler("claimegg", claim_egg))

updater.start_polling()
updater.idle()

if name == "main": main()

