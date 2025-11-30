from typing import Any

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from server.apps.core.auth.serializers.login import LoginSerializer


class LoginView(APIView):
    """Handle user authentication and JWT token issuing."""

    permission_classes = (AllowAny,)

    @extend_schema(
        summary="Login user and issue JWT token pair",
        description="Login user and issue JWT token pair",
        responses={
            status.HTTP_200_OK: LoginSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Invalid credentials",
                examples={
                    "application/json": {"detail": "Invalid credentials"},
                },
            ),
        },
        request=LoginSerializer,
    )
    def post(self, request: Request, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> Response:  # noqa: ARG002
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(result, status=status.HTTP_200_OK)
