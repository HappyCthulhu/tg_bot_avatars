from django.contrib import admin

from server.apps.bot.models import TelegramUser


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ("id", "telegram_id", "username", "user", "is_premium")
    list_filter = ("is_premium", "added_to_attachment_menu", "allow_write_to_pm")
    list_select_related = ("user",)
    search_fields = ("telegram_id", "username", "first_name", "last_name")
