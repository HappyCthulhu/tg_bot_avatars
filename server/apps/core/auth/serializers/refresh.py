from typing import Any

from rest_framework import serializers

from server.apps.core.auth.services import JWTService


class RefreshSerializer(serializers.Serializer):
    """Serializer for issuing new access token from refresh token."""

    refresh = serializers.CharField()

    def create(self, validated_data: dict[str, Any]) -> dict[str, Any]:
        refresh_token = validated_data["refresh"]
        new_access = JWTService.issue_new_access_from_refresh(refresh_token)
        return {"access": new_access}
