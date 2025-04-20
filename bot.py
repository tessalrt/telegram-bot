import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import requests

# Логи
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен твоего бота
TOKEN = "8132823364:AAFAJ-oRClVSLk5g17_CyG2EkKfhuyuuwZc"

# URL для webhook
WEBHOOK_URL = "https://<your-render-app-name>.render.com/"  # Замените на URL вашего Render-приложения

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Привет! Это тестовый бот.")

def main():
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()

    # Добавляем обработчик для команды /start
    application.add_handler(CommandHandler("start", start))

    # Устанавливаем webhook
    application.bot.set_webhook(WEBHOOK_URL + TOKEN)

    # Запускаем webhook
    application.run_webhook(listen="0.0.0.0", port=int(os.environ.get("PORT", 8000)), url_path=TOKEN, webhook_url=WEBHOOK_URL + TOKEN)

if __name__ == "__main__":
    main()
