from django.db import models

from server.apps.core.models.base import BaseModel
from server.apps.users.models.user import User


class TelegramUser(BaseModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="telegram_profile",
        verbose_name="Пользователь системы",
    )
    telegram_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID")
    username = models.CharField(max_length=255, null=True, blank=True, verbose_name="Username")
    first_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Имя")
    last_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Фамилия")
    language_code = models.CharField(max_length=20, null=True, blank=True, verbose_name="Код языка")
    is_premium = models.BooleanField(default=False, verbose_name="Премиум")
    photo_url = models.TextField(null=True, blank=True, verbose_name="URL фото")
    added_to_attachment_menu = models.BooleanField(default=False, verbose_name="Добавлен в attachment menu")
    allow_write_to_pm = models.BooleanField(default=True, verbose_name="Разрешена запись в PM")
    last_auth_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата последней авторизации")
    last_query_id = models.CharField(max_length=255, null=True, blank=True, verbose_name="Последний query id")
    last_start_param = models.CharField(max_length=255, null=True, blank=True, verbose_name="Последний start param")

    class Meta:
        ordering = ("id",)
        verbose_name = "Профиль Telegram пользователя"
        verbose_name_plural = "Профили Telegram пользователей"

    def __str__(self) -> str:
        return f"Telegram user {f"@{self.username}" if self.username else f"#{self.telegram_id}"}"
