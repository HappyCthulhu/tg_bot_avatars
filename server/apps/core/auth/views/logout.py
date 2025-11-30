from typing import Any

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class LogoutView(APIView):
    """Stateless logout endpoint.

    In stateless JWT approach server does not store token state, so logout
    is effectively handled on the client side by discarding tokens.
    This endpoint exists for API symmetry and possible future extensions.
    """

    permission_classes = (AllowAny,)

    def post(self, request: Request, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> Response:  # noqa: ARG002
        return Response(status=status.HTTP_204_NO_CONTENT)
