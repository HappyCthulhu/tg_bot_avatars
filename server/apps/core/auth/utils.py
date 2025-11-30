from __future__ import annotations

from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from rest_framework.request import Request

AUTHORIZATION_HEADER: Final[str] = "HTTP_AUTHORIZATION"
BEARER_PREFIX: Final[str] = "Bearer "


def get_authorization_header(request: Request) -> str | None:
    """Return value of Authorization header if present."""
    auth_header = request.META.get(AUTHORIZATION_HEADER)
    if not auth_header:
        return None
    return str(auth_header)


def get_bearer_token_from_request(request: Request) -> str | None:
    """Extract bearer token from request Authorization header."""
    header_value = get_authorization_header(request)
    if not header_value:
        return None

    if not header_value.startswith(BEARER_PREFIX):
        return None

    token = header_value[len(BEARER_PREFIX) :].strip()
    return token or None
