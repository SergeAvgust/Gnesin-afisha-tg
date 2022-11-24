from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

import logging

from scrapper import Scrapper
from secure import API_KEY


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# GLOBAL VARIABLES
Concerts = Scrapper()
default_message = """Если ты хочешь получить расписание на неделю - нажми /menu
Если тебе нужно расписание на определенную дату - напиши ее в чат в формате ДД.ММ
(где ДД - число, а ММ - месяц, например, 03.09 - третье сентября)"""

def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я могу рассказать, какие события произойдут в Гнесинке в ближайший месяц" + "\n" + default_message)

def echo(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

def menu(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton('Текущая неделя', callback_data='0')],
        [InlineKeyboardButton('Следующая неделя', callback_data='1')],
        [InlineKeyboardButton('Через неделю', callback_data='2')],
        [InlineKeyboardButton('Через две недели', callback_data='3')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Какое расписание тебя интересует?', reply_markup=reply_markup)

def date(update: Update, context: CallbackContext):
    message = Concerts.get_day(update.message.text)
    context.bot.send_message(chat_id=update.effective_chat.id, parse_mode='HTML', disable_web_page_preview=True, text=message)
    context.bot.send_message(chat_id=update.effective_chat.id, text=default_message)

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    msg = 'Упс! Что-то пошло не так...'
    if query.data == '0':
        msg = 'Расписание на текущую неделю:'
    elif query.data == '1':
        msg = 'Расписание на следующую неделю:'
    elif query.data == '2':
        msg = 'Расписание через неделю:'
    elif query.data == '3':
        msg = 'Расписание через две недели:'

    query.answer()
    query.edit_message_text(text=msg)
    messages = Concerts.get_week(query.data)
    for message in messages:
        context.bot.send_message(chat_id=update.effective_chat.id, parse_mode='HTML', disable_web_page_preview=True, text=message[1])
    
    context.bot.send_message(chat_id=update.effective_chat.id, text=default_message)


def main():
    updater = Updater(token=API_KEY, use_context=True)
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('menu', menu))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), date))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
    
