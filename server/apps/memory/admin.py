from django.contrib import admin

from server.apps.memory.models import MemoryFact


@admin.register(MemoryFact)
class AvatarFactAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "avatar", "created_at")
    list_filter = ("avatar", "created_at")
    list_select_related = ("user", "avatar")
    search_fields = ("text",)
