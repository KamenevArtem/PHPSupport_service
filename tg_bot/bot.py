from environs import Env
import telebot
from telebot.types import (InlineKeyboardMarkup,
                           InlineKeyboardButton,
                           ReplyKeyboardMarkup,
                           KeyboardButton)
from telebot.handler_backends import StatesGroup, State
from telebot import StateMemoryStorage
from django.utils import timezone
from django.db import DatabaseError
from tg_bot.models import Administrator, Client, Contractor, ServiceCallPrice


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
state_storage = StateMemoryStorage()
telegram_api_key = env("TELEGRAM_API_KEY", state_storage=state_storage)
bot = telebot.TeleBot(token=telegram_api_key)


class AppFlowStates(StatesGroup):
    registration = State()
    client = State()
    contractor = State()


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


registration_buttons = InlineKeyboardMarkup()
registration_buttons.add(InlineKeyboardButton("Получить помощь",
                                              callback_data="get_help"))
registration_buttons.add(InlineKeyboardButton("Стать клиентом",
                                              callback_data="become_client"))
registration_buttons.add(InlineKeyboardButton("Сотрудничество",
                                              callback_data="become_"
                                              "contractor"))

client_registration_buttons = InlineKeyboardMarkup()
client_registration_buttons.add(InlineKeyboardButton(
                                        "Условия работы и оплаты",
                                        callback_data="client_terms_of_use"))
client_registration_buttons.add(InlineKeyboardButton(
                                        "Как оплатить подписку",
                                        callback_data="how_to_get_sub"))
client_registration_buttons.add(InlineKeyboardButton(
                                        "Я оплатил, выдайте доступ",
                                        callback_data="request_client_access"))

contractor_registration_buttons = InlineKeyboardMarkup()
contractor_registration_buttons.add(InlineKeyboardButton(
                                    "Условия работы и оплаты",
                                    callback_data="contractor_terms_of_use"))
contractor_registration_buttons.add(InlineKeyboardButton(
                                    "Отправить заявку",
                                    callback_data="request_contractor_verify"))


@bot.message_handler(func=lambda message:
                     bot.get_state(message.from_user.id) is None)
@bot.message_handler(commands=['start'],
                     func=lambda message:
                     bot.get_state(message.from_user.id) is None)
def greet_unregistered(message):
    bot.set_state(message.from_user.id, AppFlowStates.registration,
                  message.chat.id)
    bot.send_message(message.chat.id, "Проект PHP Support приветствует Вас!",
                     reply_markup=registration_buttons)


@bot.message_handler(func=lambda message:
                     bot.get_state(message.from_user.id) ==
                     "AppFlowStates:registration")
def notify_to_use_buttons(message):
    bot.send_message(message.chat.id, "Используйте кнопки выше по чату, "
                     "со мной можно взаимодействовать только при "
                     "помощи них.")


@bot.callback_query_handler(func=lambda call:
                            bot.get_state(call.from_user.id) ==
                            str(AppFlowStates.registration))
def route_in_registration(call):
    match call.data:
        case "get_help":
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("Стать клиентом",
                       callback_data="become_client"))
            markup.add(InlineKeyboardButton("Сотрудничество",
                       callback_data="become_contractor"))
            bot.edit_message_text("Вы можете оставить заявку в простой "
                                  "словесной форме и мы выполним ее в "
                                  "кратчайший срок, уведомляя вас о всех "
                                  "этапах исполнения.",
                                  call.message.chat.id,
                                  call.message.message_id,
                                  reply_markup=markup)
        case "become_client":
            bot.edit_message_text("Всего несколько шагов: ",
                                  call.message.chat.id,
                                  call.message.message_id,
                                  reply_markup=client_registration_buttons)
        case "client_terms_of_use":
            bot.edit_message_text("Все просто: вы оставляете "
                                  "заявку, в кратчайший срок наш "
                                  "сотрудник берется за ее выполнение, "
                                  "сообщая срок исполнения.",
                                  call.message.chat.id,
                                  call.message.message_id,
                                  reply_markup=client_registration_buttons)
        case "how_to_get_sub":
            bot.edit_message_text("Для оплаты подписки "
                                  "перечислите сумму xxx руб на "
                                  "карту yyyy yyyy yyyy yyyy, "
                                  "указав в комментарии ваш telegram-username.",
                                  call.message.chat.id,
                                  call.message.message_id,
                                  reply_markup=client_registration_buttons)
        case "request_client_access":
            try:
                Client.objects.create(telegram_id=call.from_user.id,
                                      name=f"{call.from_user.first_name} "
                                      f"{call.from_user.last_name}",
                                      payment_confirmation_request=True)
                markup = ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(KeyboardButton("Привет, PHP Support!"))
                bot.delete_message(call.message.chat.id,
                                   call.message.message_id)
                bot.send_message(call.message.chat.id,
                                 text="Спасибо за доверие! "
                                      "Администраторы проверят ваш платеж. "
                                      "Вы получите сообщение как доступ "
                                      "будет предоставлен.",
                                      reply_markup=markup)
                bot.set_state(call.from_user.id, AppFlowStates.client,
                              call.message.chat.id)
                notify_admins("Новый запрос на подтверждение оплаты. "
                              "Проверьте счет и обработайте заявку.")
            except (ValueError, DatabaseError):
                markup = ReplyKeyboardMarkup()
                markup.add(KeyboardButton("Привет, PHP Support!"))
                bot.delete_message(call.message.chat.id,
                                   call.message.message_id)
                bot.send_message(call.message.chat.id,
                                 text="Произошла ошибка! "
                                      "Разработчики уже уведомлены. "
                                      "Попробуйте позже. ",
                                      reply_markup=markup)
                bot.set_state(call.from_user.id, None,
                              call.message.chat.id)
        case "become_contractor":
            bot.edit_message_text("Вам больше не придется "
                                  "искать заказы самому!",
                                  call.message.chat.id,
                                  call.message.message_id,
                                  reply_markup=contractor_registration_buttons)
        case "contractor_terms_of_use":
            bot.edit_message_text("Каждая заявка оплачивается "
                                  "по фиксированной ставке. "
                                  "Сумма фиксируется в момент взятия заявки, "
                                  "выплаты производятся раз в месяц.",
                                  call.message.chat.id,
                                  call.message.message_id,
                                  reply_markup=contractor_registration_buttons)
        case "request_contractor_verify":
            try:
                Contractor.objects.create(telegram_id=call.from_user.id,
                                          name=f"{call.from_user.first_name} "
                                          f"{call.from_user.last_name}",
                                          validation_request=True)
                markup = ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(KeyboardButton("Привет, PHP Support!"))
                bot.delete_message(call.message.chat.id,
                                   call.message.message_id)
                bot.send_message(call.message.chat.id,
                                 text="Спасибо за доверие! "
                                      "Руководители проекта свяжутся с Вами "
                                      "в ближайшее время для проведения "
                                      "собеседования.",
                                      reply_markup=markup)
                bot.set_state(call.from_user.id, AppFlowStates.contractor,
                              call.message.chat.id)
                notify_admins("Новый запрос на сотрудничество. "
                              "Свяжитесь с человеком и назначьте "
                              "собеседование.")
            except (ValueError, DatabaseError):
                markup = ReplyKeyboardMarkup()
                markup.add(KeyboardButton("Привет, PHP Support!"))
                bot.delete_message(call.message.chat.id,
                                   call.message.message_id)
                bot.send_message(call.message.chat.id,
                                 text="Произошла ошибка! "
                                      "Разработчики уже уведомлены. "
                                      "Попробуйте позже. ",
                                      reply_markup=markup)
                bot.set_state(call.from_user.id, None,
                              call.message.chat.id)


def notify_admins(text):
    for id in Administrator.objects.values_list('telegram_id', flat=True):
        bot.send_message(chat_id=id, text=text)
