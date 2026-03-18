from django.db import models

from server.apps.core.models.base import BaseModel


class Avatar(BaseModel):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name="Название")
    active = models.BooleanField(default=False, verbose_name="Активен")
    system_prompt = models.TextField(verbose_name="Системный промпт")

    class Meta:
        ordering = ("id",)
        verbose_name = "Аватар"
        verbose_name_plural = "Аватары"

    def __str__(self) -> str:
        return self.name
