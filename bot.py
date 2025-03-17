import json
import os
from datetime import datetime, timedelta
from flask import Flask, request
from telegram import Update, Bot, ChatMember, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Gunakan Environment Variables dari Railway
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME")
FORWARD_GROUP_ID = int(os.getenv("FORWARD_GROUP_ID"))
SUBSCRIPTION_CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Contoh: https://your-app-name.up.railway.app/webhook

# Dictionary untuk membatasi penggunaan command
usage_counts = {}
RESET_TIME = timedelta(days=1)
MAX_USES_PER_DAY = 5

# Flask Server untuk Webhook
app = Flask(__name__)

# Telegram Bot Setup
bot = Bot(token=TOKEN)
tg_app = Application.builder().token(TOKEN).build()

# Commands
async def startCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! This BOT is running on Railway.')

async def donateCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Support us by donating:\n\n"
        "🔹 BTC: 3FkQxR2muP2Z3eW8UQ1UqyQ14MudknKHwU\n"
        "🔹 SEA BANK: 901366147681\n\n"
        "Thank you! ❤️"
    )

async def menfessCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📢 *Menfess Submission*\n\n"
        "Send a message or photo/video to forward.\n\n"
        "_Make sure it follows the rules!_", parse_mode="Markdown"
    )
    return 1

async def forwardMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text:
        await bot.send_message(chat_id=FORWARD_GROUP_ID, text=update.message.text)
        await bot.send_message(chat_id=SUBSCRIPTION_CHANNEL_ID, text=update.message.text)
    elif update.message.photo:
        await bot.send_photo(chat_id=FORWARD_GROUP_ID, photo=update.message.photo[-1].file_id, caption=update.message.caption)
        await bot.send_photo(chat_id=SUBSCRIPTION_CHANNEL_ID, photo=update.message.photo[-1].file_id, caption=update.message.caption)

    await update.message.reply_text("Your message has been forwarded.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Menfess command cancelled.")
    return ConversationHandler.END

# Webhook Handler
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), bot)
    tg_app.process_update(update)
    return "OK", 200

# Setup Routes
@app.route('/')
def index():
    return "Bot is running on Railway 🚀"

if __name__ == '__main__':
    # Setup Command Handlers
    tg_app.add_handler(CommandHandler('start', startCommand))
    tg_app.add_handler(CommandHandler('donate', donateCommand))

    # Menfess Command
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('menfess', menfessCommand)],
        states={1: [MessageHandler(filters.TEXT | filters.PHOTO, forwardMessage)]},
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    tg_app.add_handler(conv_handler)

    # Set Webhook
    tg_app.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")

    # Run Flask Server
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
