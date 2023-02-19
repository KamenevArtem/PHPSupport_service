from django.db import models


class Administrator(models.Model):
    telegram_id = models.PositiveBigIntegerField(verbose_name="Телеграм ID",
                                                 primary_key=True)
    name = models.CharField(verbose_name="Имя",
                            max_length=100)

    def __str__(self):
        return f"{self.name}"


class Client(models.Model):
    telegram_id = models.PositiveBigIntegerField(verbose_name="Телеграм ID",
                                                 primary_key=True)
    name = models.CharField(verbose_name="Имя",
                            max_length=100)
    subscription_estimate_date = models.DateTimeField(
                                 verbose_name="Дата окончания подписки",
                                 auto_now_add=True)
    payment_confirmation_request = models.BooleanField(
                                 verbose_name="Запрос на подтверждение оплаты",
                                 default=False)

    def __str__(self):
        return f"{self.name}"


class Contractor(models.Model):
    telegram_id = models.PositiveBigIntegerField(verbose_name="Телеграм ID",
                                                 primary_key=True)
    name = models.CharField(verbose_name="Имя",
                            max_length=100)
    validation_status = models.BooleanField(
                               verbose_name="Статус сотрудничества",
                               default=False)
    validation_request = models.BooleanField(
                               verbose_name="Запрос на сотрудничество",
                               default=False)

    def __str__(self):
        return f"{self.name} - {self.telegram_id}"


class FinPlanning(models.Model):
    administrator = models.ForeignKey(Administrator,
                                      on_delete=models.PROTECT,
                                      verbose_name="Администратор")
    date = models.DateTimeField(verbose_name="Дата проведения",
                                auto_now_add=True)

    def __str__(self):
        return f"{self.administrator} - {self.date}"


class ServiceCallPrice(models.Model):
    administrator = models.ForeignKey(Administrator,
                                      on_delete=models.PROTECT,
                                      verbose_name="Администратор")
    price = models.IntegerField(verbose_name="Стоимость исполнения заявки")
    date = models.DateTimeField(verbose_name="Дата установки",
                                auto_now_add=True)

    def __str__(self):
        return f"{self.price}"


class ServiceCall(models.Model):
    client = models.ForeignKey(Client,
                               on_delete=models.PROTECT,
                               verbose_name="Клиент")
    contractor = models.ForeignKey(Contractor,
                                   on_delete=models.PROTECT,
                                   verbose_name="Подрядчик",
                                   null=True,
                                   blank=True)
    creation_date = models.DateTimeField(verbose_name="Дата создания",
                                         auto_now_add=True)
    estimate_time = models.DateTimeField(verbose_name="Дата готовности",
                                         null=True,
                                         blank=True)
    description = models.TextField(verbose_name="Описание")
    completion_status = models.BooleanField(verbose_name="Выполнена",
                                            default=False)
    price = models.ForeignKey(ServiceCallPrice,
                              on_delete=models.PROTECT,
                              verbose_name="Стоимость")
    paid = models.BooleanField(verbose_name="Оплачена",
                               default=False)

    def __str__(self):
        return f"{self.id} - {self.client}"


class Question(models.Model):
    service_call = models.ForeignKey(ServiceCall,
                                     on_delete=models.PROTECT,
                                     verbose_name="Заявка")
    question = models.TextField(verbose_name="Вопрос")
    answer = models.TextField(verbose_name="Ответ")

    def __str__(self):
        return f"{self.service_call} - {self.question}"
