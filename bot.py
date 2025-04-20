import logging
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import requests

# Логи
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен твоего бота
TOKEN = "8132823364:AAFAJ-oRClVSLk5g17_CyG2EkKfhuyuuwZc"

# URL для webhook
WEBHOOK_URL = "https://<your-render-app-name>.render.com/"  # Замените на URL вашего Render-приложения

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет! Это тестовый бот.")

def main():
    # Получаем диспетчер и добавляем обработчики
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))

    # Устанавливаем webhook
    updater.bot.setWebhook(WEBHOOK_URL + TOKEN)

    # Запускаем бота
    updater.start_webhook(listen="0.0.0.0", port=int(os.environ.get('PORT', 8000)),
                          url_path=TOKEN, webhook_url=WEBHOOK_URL + TOKEN)

    updater.idle()

if __name__ == '__main__':
    main()
