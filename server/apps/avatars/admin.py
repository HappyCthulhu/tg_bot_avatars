from django.contrib import admin

from server.apps.avatars.models import Avatar


@admin.register(Avatar)
class AvatarAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "active")
    list_filter = ("active",)
    list_editable = ("active",)
    search_fields = ("name",)
