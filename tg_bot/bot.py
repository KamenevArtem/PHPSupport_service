from environs import Env
import telebot
from django.utils import timezone
from tg_bot.models import Administrator, Client, Contractor


class ClientActiveSubscriptionFilter(telebot.SimpleCustomFilter):
    key = "client_active_subscription"

    @staticmethod
    def check(message):
        now = timezone.now()
        try:
            Client.objects.get(telegram_id=message.from_user.id,
                               subscription_estimate_date__gte=now)
            return True
        except Client.DoesNotExist:
            return False


class ClientPaymentConfirmationFilter(telebot.SimpleCustomFilter):
    key = "client_payment_confirmation"

    @staticmethod
    def check(message):
        try:
            Client.objects.get(telegram_id=message.from_user.id,
                               payment_confirmation_request=True)
            return True
        except Client.DoesNotExist:
            return False


class ClientInactiveSubscriptionFilter(telebot.SimpleCustomFilter):
    key = "client_inactive_subscription"

    @staticmethod
    def check(message):
        now = timezone.now()
        try:
            Client.objects.get(telegram_id=message.from_user.id,
                               subscription_estimate_date__lte=now)
            return True
        except Client.DoesNotExist:
            return False


class ContractorWithValidationFilter(telebot.SimpleCustomFilter):
    key = "contractor_with_validation"

    @staticmethod
    def check(message):
        try:
            Contractor.objects.get(telegram_id=message.from_user.id,
                                   validation_status=True)
            return True
        except Contractor.DoesNotExist:
            return False


class ContractorValidationRequestFilter(telebot.SimpleCustomFilter):
    key = "contractor_validation_request"

    @staticmethod
    def check(message):
        try:
            Contractor.objects.get(telegram_id=message.from_user.id,
                                   validation_request=True)
            return True
        except Contractor.DoesNotExist:
            return False


class ContractorNoValidationFilter(telebot.SimpleCustomFilter):
    key = "contractor_no_validation"

    @staticmethod
    def check(message):
        try:
            Contractor.objects.get(telegram_id=message.from_user.id,
                                   validation_status=False)
            return True
        except Contractor.DoesNotExist:
            return False


class AdministratorFilter(telebot.SimpleCustomFilter):
    key = "administrator"

    @staticmethod
    def check(message):
        try:
            Administrator.objects.get(telegram_id=message.from_user.id)
            return True
        except Administrator.DoesNotExist:
            return False


env = Env()
env.read_env()
telegram_api_key = env("TELEGRAM_API_KEY")
bot = telebot.TeleBot(token=telegram_api_key)

bot.add_custom_filter(AdministratorFilter())
bot.add_custom_filter(ClientActiveSubscriptionFilter())
bot.add_custom_filter(ClientPaymentConfirmationFilter())
bot.add_custom_filter(ClientInactiveSubscriptionFilter())
bot.add_custom_filter(ContractorWithValidationFilter())
bot.add_custom_filter(ContractorValidationRequestFilter())
bot.add_custom_filter(ContractorNoValidationFilter())


@bot.message_handler(client_active_subscription=True)
def greet_active_subscription_client(message):
    bot.reply_to(message, "Привет, клиент с активной подпиской!")


@bot.message_handler(client_payment_confirmation=True)
def greet_payment_confirmation(message):
    bot.reply_to(message, "Привет, клиент, запрос на оплату рассматривается!")


@bot.message_handler(client_inactive_subscription=True)
def greet_inactive_subscription(message):
    bot.reply_to(message, "Привет, клиент с неактивной подпиской!")


@bot.message_handler(contractor_with_validation=True)
def greet_contractor_with_validation(message):
    bot.reply_to(message, "Привет, подрядчик с валидацией!")


@bot.message_handler(contractor_validation_request=True)
def greet_contractor_validation_request(message):
    bot.reply_to(message, "Привет, подрядчик, ожидай утверждения валидации!")


@bot.message_handler(contractor_no_validation=True)
def greet_contractor_no_validation(message):
    bot.reply_to(message, "Привет, подрядчик без валидации!")


@bot.message_handler(administrator=True)
def greet_admin(message):
    bot.reply_to(message, "Привет, администратор!")


@bot.message_handler(commands=['start', 'hey'])
def send_welcome(message):
    bot.reply_to(message, f"{message.from_user.id}")
