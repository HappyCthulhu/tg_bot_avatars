from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from server.apps.core.auth.serializers.refresh import RefreshSerializer


class RefreshView(APIView):
    """Issue new access token from refresh token."""

    permission_classes = (AllowAny,)

    @extend_schema(
        summary="Issue new access token from refresh token",
        description="Issue new access token from refresh token",
        responses={
            status.HTTP_200_OK: RefreshSerializer,
        },
        request=RefreshSerializer,
    )
    def post(self, request: Request, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> Response:  # noqa: ARG002
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(result, status=status.HTTP_200_OK)
