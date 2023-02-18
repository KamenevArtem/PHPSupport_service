from django.core.management.base import BaseCommand, CommandError
from tg_bot.bot import bot

class Command(BaseCommand):
    help = 'Run bot'

    def handle(self, *args, **options):
        bot.infinity_polling()
