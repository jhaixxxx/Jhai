// index.js
const TelegramBot = require('node-telegram-bot-api');
const puppeteer = require('puppeteer-core');
const chromium = require('chrome-aws-lambda');

// Telegram Bot Config
const token = 'YOUR_BOT_TOKEN';  // Replace with your bot's token
const bot = new TelegramBot(token, { polling: true });
const ADMIN_ID = YOUR_ADMIN_ID;  // Replace with your Telegram ID

// Puppeteer Setup
async function launchBrowser() {
  const browser = await puppeteer.launch({
    headless: true,
    executablePath: await chromium.executablePath,
    args: chromium.args,
    defaultViewport: chromium.defaultViewport,
  });
  return browser;
}

// Random user generation
function getRandomUsername() {
  return 'User' + Math.floor(Math.random() * 900000 + 100000);
}

function getRandomPhone() {
  return '09' + Math.floor(Math.random() * 900000000 + 100000000);
}

// Function to register user
async function registerUser(page) {
  await page.goto('https://www.jiliwin55.com/m/register');
  await page.waitForTimeout(3000);

  const username = getRandomUsername();
  const password = 'Password123';

  await page.type('input[name="username"]', username);
  await page.type('input[name="password"]', password);
  await page.type('input[name="confimpsw"]', password);
  await page.click('.submit-btn');

  await page.waitForTimeout(2000);
  return { username, password };
}

// Function to bind bank account
async function bindBank(page) {
  await page.goto('https://www.jiliwin55.com/m/securityCenter/addBankCardPix');
  await page.waitForTimeout(3000);

  await page.type('input[name="payee"]', 'John Doe');
  await page.type('input[name="customField"]', getRandomPhone());
  await page.type('input[name="withdraw"]', '000000');
  await page.type('input[name="withdrawT"]', '000000');
  await page.click('.am-button.btn-success');

  await page.waitForTimeout(2000);
  return 'Bank binding successful!';
}

// Function to claim reward
async function claimReward(page) {
  await page.goto('https://www.jiliwin55.com/m/home');
  await page.waitForTimeout(3000);

  try {
    const claimButton = await page.$('.item-claim');
    if (claimButton) {
      await claimButton.click();
      await page.waitForTimeout(2000);
      return 'Reward claimed successfully!';
    } else {
      return 'No claimable rewards found.';
    }
  } catch (error) {
    return 'Error claiming reward.';
  }
}

// Telegram Commands
bot.onText(/\/start/, (msg) => {
  bot.sendMessage(msg.chat.id, 'Welcome! Use /help for instructions.');
});

bot.onText(/\/help/, (msg) => {
  bot.sendMessage(msg.chat.id, 'Commands:\n/register - Register a new user\n/bindbank - Bind bank details\n/claim - Claim rewards');
});

bot.onText(/\/generate/, async (msg) => {
  bot.sendMessage(msg.chat.id, 'Starting the process...');

  const browser = await launchBrowser();
  const page = await browser.newPage();

  // Register User
  const { username, password } = await registerUser(page);
  bot.sendMessage(msg.chat.id, `✅ Registered: ${username}\n🔑 Password: ${password}`);

  // Bind Bank Account
  const bindResult = await bindBank(page);
  bot.sendMessage(msg.chat.id, bindResult);

  // Claim Reward
  const rewardResult = await claimReward(page);
  bot.sendMessage(msg.chat.id, rewardResult);

  await browser.close();
});

console.log('Bot is running...');
