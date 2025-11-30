from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any, Final

import jwt
from django.conf import settings
from django.utils import timezone as django_timezone

from server.apps.core.auth import constants
from server.apps.core.auth.exceptions import InvalidTokenError, TokenExpiredError
from server.apps.core.models.user import User


class JWTService:
    """Service for creating and validating JWT access and refresh tokens."""

    _ALGORITHM: Final[str] = settings.JWT_ALGORITHM
    _SECRET_KEY: Final[str] = settings.JWT_SECRET_KEY
    _ACCESS_LIFETIME: Final[timedelta] = settings.JWT_ACCESS_LIFETIME
    _REFRESH_LIFETIME: Final[timedelta] = settings.JWT_REFRESH_LIFETIME
    _ISSUER: Final[str | None] = getattr(settings, "JWT_ISSUER", None)
    _AUDIENCE: Final[str | None] = getattr(settings, "JWT_AUDIENCE", None)

    @classmethod
    def _make_exp(cls, lifetime: timedelta) -> datetime:
        return django_timezone.now() + lifetime

    @classmethod
    def _build_base_payload(cls, user_id: int, token_type: str, lifetime: timedelta) -> dict[str, Any]:
        now = django_timezone.now()
        exp = cls._make_exp(lifetime)

        payload: dict[str, Any] = {
            constants.SUBJECT_FIELD: str(user_id),
            constants.TOKEN_TYPE_FIELD: token_type,
            "iat": int(now.replace(tzinfo=UTC).timestamp()),
            "exp": int(exp.replace(tzinfo=UTC).timestamp()),
        }

        if cls._ISSUER:
            payload["iss"] = cls._ISSUER
        if cls._AUDIENCE:
            payload["aud"] = cls._AUDIENCE

        return payload

    @classmethod
    def create_access_token(cls, user: User) -> str:
        """Create signed access token for user."""
        payload = cls._build_base_payload(
            user_id=user.pk,
            token_type=constants.ACCESS_TOKEN_TYPE,
            lifetime=cls._ACCESS_LIFETIME,
        )
        return jwt.encode(payload, cls._SECRET_KEY, algorithm=cls._ALGORITHM)

    @classmethod
    def create_refresh_token(cls, user: User) -> str:
        """Create signed refresh token for user."""
        payload = cls._build_base_payload(
            user_id=user.pk,
            token_type=constants.REFRESH_TOKEN_TYPE,
            lifetime=cls._REFRESH_LIFETIME,
        )
        return jwt.encode(payload, cls._SECRET_KEY, algorithm=cls._ALGORITHM)

    @classmethod
    def create_token_pair(cls, user: User) -> dict[str, str]:
        """Create token pair (access and refresh) for user."""
        return {
            "access": cls.create_access_token(user),
            "refresh": cls.create_refresh_token(user),
        }

    @classmethod
    def decode_token(cls, token: str, expected_type: str | None = None) -> dict[str, Any]:
        """Decode and validate token.

        Raises:
            TokenExpiredError: if token is expired.
            InvalidTokenError: if token is invalid for any other reason.

        """
        try:
            decoded = jwt.decode(
                token,
                cls._SECRET_KEY,
                algorithms=[cls._ALGORITHM],
                issuer=cls._ISSUER,
                audience=cls._AUDIENCE,
            )
        except jwt.ExpiredSignatureError as exc:
            raise TokenExpiredError("Token has expired") from exc
        except jwt.InvalidTokenError as exc:
            raise InvalidTokenError("Invalid token") from exc

        token_type = decoded.get(constants.TOKEN_TYPE_FIELD)
        if expected_type is not None and token_type != expected_type:
            raise InvalidTokenError("Invalid token type")

        return decoded

    @classmethod
    def issue_new_access_from_refresh(cls, refresh_token: str) -> str:
        """Issue new access token based on valid refresh token."""
        payload = cls.decode_token(refresh_token, expected_type=constants.REFRESH_TOKEN_TYPE)

        try:
            user_id = int(payload[constants.SUBJECT_FIELD])
        except (KeyError, ValueError) as exc:
            raise InvalidTokenError("Invalid subject in token") from exc

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist as exc:
            raise InvalidTokenError("User not found for given token") from exc

        if not user.is_active:
            raise InvalidTokenError("User is inactive")

        return cls.create_access_token(user)
