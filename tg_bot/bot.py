from environs import Env
from telegram import Bot
from telegram import Update
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.ext import CallbackQueryHandler


def get_registration_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(text='Подробнее о проекте',
                                 callback_data='extended_project_info_button')
        ],
        [
            InlineKeyboardButton(text='Стать клиентом',
                                 callback_data='become_client_button')
        ],
        [
            InlineKeyboardButton(text='Сотрудничество',
                                 callback_data='become_contractor_button')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_detailed_company_info_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(text='Стать клиентом',
                                 callback_data='become_client_button')
        ],
        [
            InlineKeyboardButton(text='Сотрудничество',
                                 callback_data='become_contractor_button')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_become_client_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(text='Условия предоставления услуг',
                                 callback_data='client_termsofservice_button')
        ],
        [
            InlineKeyboardButton(text='Как оплатить подписку',
                                 callback_data='client_howtopay_button')
        ],
        [
            InlineKeyboardButton(text='Я оплатил, выдайте доступ',
                                 callback_data='client_getaccess_button')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def keyboard_callback_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data

    match data:
        case 'extended_project_info_button':
            query.edit_message_text(
                text="Прям\nочень\nпродрбный\nтекст\nо\nкомпании\nс\nHTML\n"
                     "форматированием",
                reply_markup=get_detailed_company_info_keyboard()
            )
        case 'become_client_button':
            query.edit_message_text(
                text="Приветственная маркетинговая фраза",
                reply_markup=get_become_client_keyboard()
            )
        case 'client_termsofservice_button':
            query.edit_message_text(
                text="Очень\nпродрбный\nтекс\nо\nусловиями\nработы\n"
                     "с\nHTML\nформатированием",
                reply_markup=get_become_client_keyboard()
            )
        case 'client_howtopay_button':
            query.edit_message_text(
                text="Очень\nпродрбная\nинструкция\nкак\nоплатить\nподписку"
                     "\nс\nHTML\nформатированием",
                reply_markup=get_become_client_keyboard()
            )
        case 'client_getaccess_button':
            query.message.delete()
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Спасибо за доверие!\nМы уведомили администраторов "
                     "проекта.\nВаш аккаунт будет активирован в "
                     "ближайшие 24 часа."
            )


def process_start(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Приветствие\nи\nмного\nполезной\nинформации\nо\nпроекте",
        reply_markup=get_registration_keyboard()
    )


def process_text(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Приветствие\nи\nмного\nполезной\nинформации\nо\nпроекте",
        reply_markup=get_registration_keyboard()
    )


def run_bot():
    env = Env()
    env.read_env()
    telegram_api_key = env('TELEGRAM_API_KEY')
    bot = Bot(token=telegram_api_key)
    updater = Updater(bot=bot)

    start_handler = CommandHandler('start', process_start)
    message_handler = MessageHandler(Filters.text, process_text)
    buttons_handler = CallbackQueryHandler(callback=keyboard_callback_handler,
                                           pass_chat_data=True)

    updater.dispatcher.add_handler(start_handler)
    updater.dispatcher.add_handler(message_handler)
    updater.dispatcher.add_handler(buttons_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    run_bot()
