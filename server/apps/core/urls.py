from django.urls import path

from server.apps.core.views.health import health_check

urlpatterns = [
    path("health/", health_check, name="health"),
]
