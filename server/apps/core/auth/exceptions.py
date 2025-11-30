from __future__ import annotations

from rest_framework.exceptions import AuthenticationFailed


class InvalidTokenError(AuthenticationFailed):
    """Raised when JWT token is invalid."""


class TokenExpiredError(AuthenticationFailed):
    """Raised when JWT token is expired."""


