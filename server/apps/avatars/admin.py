from django.contrib import admin

from server.apps.avatars.models import Avatar


@admin.register(Avatar)
class AvatarAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
