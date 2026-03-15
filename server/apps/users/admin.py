from django.contrib import admin

from server.apps.users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "active_avatar", "created_at", "updated_at")
    list_select_related = ("active_avatar",)
