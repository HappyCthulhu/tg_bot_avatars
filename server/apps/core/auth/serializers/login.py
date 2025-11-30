from typing import TYPE_CHECKING, Any

from django.contrib.auth import authenticate
from rest_framework import serializers

from server.apps.core.auth.services import JWTService

if TYPE_CHECKING:
    from server.apps.core.models.user import User


class LoginSerializer(serializers.Serializer):
    """Serializer for user authentication and JWT token pair issuing."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            email=email,
            password=password,
        )

        if user is None:
            msg = "Unable to log in with provided credentials."
            raise serializers.ValidationError(msg, code="authorization")

        if not user.is_active:
            msg = "User account is disabled."
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs

    def create(self, validated_data: dict[str, Any]) -> dict[str, Any]:
        user: User = validated_data["user"]
        tokens = JWTService.create_token_pair(user)

        return {
            "access": tokens["access"],
            "refresh": tokens["refresh"],
            "user": {
                "id": user.pk,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
        }
