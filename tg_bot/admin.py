from django.contrib import admin
from tg_bot.models import (Administrator,
                           Client,
                           Contractor,
                           FinPlanning,
                           ServiceCallPrice,
                           ServiceCall,
                           Question)


@admin.register(Administrator)
class AdministratorAdmin(admin.ModelAdmin):
    list_display = ("name", "telegram_id")


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name",
                    "telegram_id",
                    "subscription_estimate_date",
                    "payment_comfirmation_request")
    fields = ("telegram_id", "name")


@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    list_display = ("name",
                    "telegram_id",
                    "validation_status",
                    "validation_request")
    fields = ("telegram_id", "name")


@admin.register(FinPlanning)
class FinPlanningAdmin(admin.ModelAdmin):
    ordering = ["id"]
    list_display = ("administrator",
                    "date")


@admin.register(ServiceCallPrice)
class ServiceCallPriceAdmin(admin.ModelAdmin):
    ordering = ["id"]
    list_display = ("price",
                    "administrator",
                    "date")


@admin.register(ServiceCall)
class ServiceCallAdmin(admin.ModelAdmin):
    ordering = ["-id"]
    list_display = ("client",
                    "creation_date",
                    "description",
                    "contractor",
                    "estimate_time",
                    "completion_status",
                    "price",
                    "paid")
    fields = ("client", "description", "price")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    ordering = ["-id"]
    list_display = ("service_call",
                    "question",
                    "answer")
    fields = ("service_call", "question")
