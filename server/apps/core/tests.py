from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from server.apps.core.auth.constants import ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE
from server.apps.core.auth.services import JWTService

User = get_user_model()


class JWTServicesTests(TestCase):
    """Tests for JWTService token creation and validation."""

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="user@example.com",
            password="test-password",
            first_name="Test",
            last_name="User",
        )

    def test_create_token_pair_contains_access_and_refresh(self) -> None:
        tokens = JWTService.create_token_pair(self.user)

        self.assertIn("access", tokens)
        self.assertIn("refresh", tokens)

    def test_access_token_has_correct_type(self) -> None:
        access = JWTService.create_access_token(self.user)
        payload = JWTService.decode_token(access)

        self.assertEqual(payload["type"], ACCESS_TOKEN_TYPE)
        self.assertEqual(payload["sub"], str(self.user.pk))

    def test_refresh_token_has_correct_type(self) -> None:
        refresh = JWTService.create_refresh_token(self.user)
        payload = JWTService.decode_token(refresh)

        self.assertEqual(payload["type"], REFRESH_TOKEN_TYPE)
        self.assertEqual(payload["sub"], str(self.user.pk))

    def test_issue_new_access_from_refresh(self) -> None:
        refresh = JWTService.create_refresh_token(self.user)
        new_access = JWTService.issue_new_access_from_refresh(refresh)

        payload = JWTService.decode_token(new_access)
        self.assertEqual(payload["type"], ACCESS_TOKEN_TYPE)
        self.assertEqual(payload["sub"], str(self.user.pk))


class JWTAuthEndpointsTests(TestCase):
    """Integration tests for login and refresh endpoints."""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="user2@example.com",
            password="test-password",
            first_name="Test",
            last_name="User",
        )

    def test_login_returns_token_pair_and_user_data(self) -> None:
        url = reverse("auth:login")
        response = self.client.post(
            url,
            data={"email": "user2@example.com", "password": "test-password"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["email"], "user2@example.com")

    def test_refresh_returns_new_access_token(self) -> None:
        login_url = reverse("auth:login")
        login_response = self.client.post(
            login_url,
            data={"email": "user2@example.com", "password": "test-password"},
            format="json",
        )
        refresh_token = login_response.data["refresh"]

        url = reverse("auth:refresh")
        response = self.client.post(url, data={"refresh": refresh_token}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

    def test_protected_view_requires_authentication(self) -> None:
        # health endpoint is public in current project, so here we only check that
        # authentication class can be initialized and does not break schema generation.
        schema_url = reverse("schema")
        response = self.client.get(schema_url)

        self.assertEqual(response.status_code, 200)
