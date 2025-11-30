from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from server.apps.core.auth import constants
from server.apps.core.auth.services import JWTService
from server.apps.core.auth.utils import get_bearer_token_from_request
from server.apps.core.models.user import User

if TYPE_CHECKING:
    from rest_framework.request import Request


class JWTAuthentication(BaseAuthentication):
    """JWT authentication backend for DRF."""

    def authenticate(self, request: Request) -> tuple[User, dict[str, Any]] | None:
        """Authenticate request using JWT access token."""
        token = get_bearer_token_from_request(request)
        if token is None:
            return None

        payload = JWTService.decode_token(token, expected_type=constants.ACCESS_TOKEN_TYPE)

        user_id = payload.get(constants.SUBJECT_FIELD)
        if user_id is None:
            raise AuthenticationFailed("Invalid token payload")

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist as exc:
            raise AuthenticationFailed("User not found") from exc

        if not user.is_active:
            raise AuthenticationFailed("User inactive or deleted")

        return user, payload
