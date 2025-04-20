import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Логи
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Google Sheets
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
gs_client = gspread.authorize(creds)
sheet = gs_client.open("Queue").sheet1

# Этапы опроса
SURNAME, NAME, DOB, PHONE, EMAIL = range(5)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Здравствуйте! Давайте оформим вашу заявку.\nВведите, пожалуйста, вашу фамилию:")
    return SURNAME

def surname_handler(update: Update, context: CallbackContext):
    context.user_data['surname'] = update.message.text.strip()
    update.message.reply_text("Отлично. Теперь введите имя:")
    return NAME

def name_handler(update: Update, context: CallbackContext):
    context.user_data['name'] = update.message.text.strip()
    update.message.reply_text("Дата рождения (в формате ДД.MM.ГГГГ):")
    return DOB

def dob_handler(update: Update, context: CallbackContext):
    context.user_data['dob'] = update.message.text.strip()
    update.message.reply_text("Телефон (например, +7XXXXXXXXXX):")
    return PHONE

def phone_handler(update: Update, context: CallbackContext):
    context.user_data['phone'] = update.message.text.strip()
    update.message.reply_text("E‑mail:")
    return EMAIL

def email_handler(update: Update, context: CallbackContext):
    # собираем все данные
    data = {
        'surname': context.user_data['surname'],
        'name':    context.user_data['name'],
        'dob':     context.user_data['dob'],
        'phone':   context.user_data['phone'],
        'email':   update.message.text.strip()
    }
    # записываем в Google Sheets
    sheet.append_row([
        data['surname'],
        data['name'],
        data['dob'],
        data['phone'],
        data['email']
    ])
    update.message.reply_text("Спасибо! Ваша заявка принята в очередь.")
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("Оформление заявки отменено.")
    return ConversationHandler.END

def main():
    # Указываем свой токен для бота
    updater = Updater("ВАШ_BOT_TOKEN", use_context=True)
    dp = updater.dispatcher

    # Конфигурация обработчиков
    conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SURNAME: [MessageHandler(Filters.text & ~Filters.command, surname_handler)],
            NAME:    [MessageHandler(Filters.text & ~Filters.command, name_handler)],
            DOB:     [MessageHandler(Filters.text & ~Filters.command, dob_handler)],
            PHONE:   [MessageHandler(Filters.text & ~Filters.command, phone_handler)],
            EMAIL:   [MessageHandler(Filters.text & ~Filters.command, email_handler)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv)

    # Старт polling, чтобы получать обновления
    updater.start_polling()

    # Ожидаем завершения работы
    updater.idle()

if __name__ == '__main__':
    main()
