from __future__ import annotations

from django.urls import path

from server.apps.core.auth.views.login import LoginView
from server.apps.core.auth.views.logout import LogoutView
from server.apps.core.auth.views.refresh import RefreshView

app_name = "auth"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshView.as_view(), name="refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
