from environs import Env
import telebot


env = Env()
env.read_env()
telegram_api_key = env('TELEGRAM_API_KEY')
bot = telebot.TeleBot(token=telegram_api_key)


@bot.message_handler(commands=['start', 'hey'])
def send_welcome(message):
    bot.reply_to(message, "Hello there!")
