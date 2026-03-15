from django.db import models

from server.apps.avatars.models.avatar import Avatar
from server.apps.core.models.base import BaseModel
from server.apps.users.models.user import User


class MemoryFact(BaseModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="facts",
        verbose_name="Пользователь",
    )
    avatar = models.ForeignKey(
        Avatar,
        on_delete=models.CASCADE,
        related_name="facts",
        verbose_name="Аватар",
    )
    text = models.TextField(verbose_name="Факт")

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Факт долгосрочной памяти"
        verbose_name_plural = "Факты долгосрочной памяти"
        indexes = (models.Index(fields=["user", "avatar"]),)

    def __str__(self) -> str:
        return f"Memory fact #{self.id}"
