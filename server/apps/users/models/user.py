from django.db import models

from server.apps.avatars.models.avatar import Avatar
from server.apps.core.models.base import BaseModel


class User(BaseModel):
    active_avatar = models.ForeignKey(
        Avatar,
        on_delete=models.SET_NULL,
        related_name="active_users",
        null=True,
        blank=True,
        verbose_name="Текущий аватар",
    )

    class Meta:
        ordering = ("id",)
        verbose_name = "Пользователь системы"
        verbose_name_plural = "Пользователи системы"

    def __str__(self) -> str:
        return f"User #{self.id}"
