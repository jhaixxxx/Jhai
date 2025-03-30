from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import random
import asyncio

# TELEGRAM BOT CONFIG
TOKEN = "7118239951:AAHN8AkMRvscPXFDmHRLVcDyL8o-5yJJuBY"
ADMIN_ID = 6735321947  # Replace with your Telegram ID

# SELENIUM CONFIG
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

# FUNCTION TO GENERATE RANDOM USER DETAILS
def get_random_username():
    return 'User' + str(random.randint(100000, 999999))

def get_random_phone():
    return '09' + str(random.randint(100000000, 999999999))

# FUNCTION TO REGISTER USERS
def register_user():
    driver.get("https://www.jiliwin55.com/m/register")
    time.sleep(3)

    username = get_random_username()
    password = "Paidsc123"

    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "confimpsw").send_keys(password)
    driver.find_element(By.CLASS_NAME, "submit-btn").click()

    time.sleep(2)
    return username, password

# FUNCTION TO BIND BANK DETAILS
def bind_bank():
    driver.get("https://www.jiliwin55.com/m/securityCenter/addBankCardPix")
    time.sleep(3)

    driver.find_element(By.NAME, "payee").send_keys("John Doe")
    driver.find_element(By.NAME, "customField").send_keys(get_random_phone())
    driver.find_element(By.NAME, "withdraw").send_keys("000000")
    driver.find_element(By.NAME, "withdrawT").send_keys("000000")
    driver.find_element(By.CLASS_NAME, "am-button.btn-success").click()

    time.sleep(2)
    return "Bank binding successful!"

# FUNCTION TO CLAIM REWARD
def claim_reward():
    driver.get("https://www.jiliwin55.com/m/home")
    time.sleep(3)

    try:
        claim_button = driver.find_element(By.CLASS_NAME, "item-claim")
        claim_button.click()
        time.sleep(2)
        return "Reward claimed successfully!"
    except:
        return "No claimable rewards found."

# TELEGRAM COMMAND HANDLERS
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome! Use /register, /bindbank, or /claim to perform actions.")

async def register(update: Update, context: CallbackContext):
    username, password = register_user()
    await update.message.reply_text(f"✅ Registered: {username}\n🔑 Password: {password}")

async def bind(update: Update, context: CallbackContext):
    result = bind_bank()
    await update.message.reply_text(f"{result}")

async def claim(update: Update, context: CallbackContext):
    result = claim_reward()
    await update.message.reply_text(f"{result}")

# TELEGRAM BOT SETUP
async def main():
    # Initialize Application instead of Updater
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("register", register))
    application.add_handler(CommandHandler("bindbank", bind))
    application.add_handler(CommandHandler("claim", claim))

    # Run the bot
    await application.run_polling()

# If already inside an asynchronous environment, run main without asyncio.run
if __name__ == "__main__":
    import sys
    if sys.stdout.isatty():
        asyncio.run(main())
    else:
        # Use this when running in environments like Render or others where the loop is running
        loop = asyncio.get_event_loop()
        loop.create_task(main())
        loop.run_forever()
