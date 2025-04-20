import logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ConversationHandler,
    ContextTypes, filters
)
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Логи
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Google Sheets
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
import os
import json
from oauth2client.service_account import ServiceAccountCredentials

# Чтение данных из переменной окружения
credentials_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')

if credentials_json:
    credentials_dict = json.loads(credentials_json)
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
else:
    print("Ошибка: переменная окружения GOOGLE_APPLICATION_CREDENTIALS_JSON не установлена.")
    exit(1)
gs_client = gspread.authorize(creds)
sheet = gs_client.open("Queue").sheet1

# Этапы опроса
SURNAME, NAME, DOB, PHONE, EMAIL = range(5)

# Хендлеры опроса
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Здравствуйте! Давайте оформим вашу заявку.\nВведите, пожалуйста, вашу фамилию:")
    return SURNAME

async def surname_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['surname'] = update.message.text.strip()
    await update.message.reply_text("Отлично. Теперь введите имя:")
    return NAME

async def name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text.strip()
    await update.message.reply_text("Дата рождения (в формате ДД.MM.ГГГГ):")
    return DOB

async def dob_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['dob'] = update.message.text.strip()
    await update.message.reply_text("Телефон (например, +7XXXXXXXXXX):")
    return PHONE

async def phone_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text.strip()
    await update.message.reply_text("E‑mail:")
    return EMAIL

async def email_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = {
        'surname': context.user_data['surname'],
        'name':    context.user_data['name'],
        'dob':     context.user_data['dob'],
        'phone':   context.user_data['phone'],
        'email':   update.message.text.strip()
    }

    # Запись в Google Sheets
    sheet.append_row([
        data['surname'],
        data['name'],
        data['dob'],
        data['phone'],
        data['email']
    ])

    await update.message.reply_text("Спасибо! Ваша заявка принята в очередь.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Оформление заявки отменено.")
    return ConversationHandler.END

# Основная функция
def main():
    TOKEN = "8132823364:AAFAJ-oRClVSLk5g17_CyG2EkKfhuyuuwZc"

    app = Application.builder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SURNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, surname_handler)],
            NAME:    [MessageHandler(filters.TEXT & ~filters.COMMAND, name_handler)],
            DOB:     [MessageHandler(filters.TEXT & ~filters.COMMAND, dob_handler)],
            PHONE:   [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_handler)],
            EMAIL:   [MessageHandler(filters.TEXT & ~filters.COMMAND, email_handler)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(conv)

    app.run_polling()

if __name__ == '__main__':
    main()
