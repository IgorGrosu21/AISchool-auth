from typing import Any

from rest_framework import serializers

from api.models import User

from ..fields import CodeField, EmailField


class UserEmailSerializer(serializers.Serializer[User]):
    email = EmailField(write_only=True, allow_blank=True, allow_null=True)
    type = serializers.ChoiceField(choices=["primary", "backup"], write_only=True)
    code = CodeField(write_only=True, required=False, allow_blank=True, allow_null=True)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if attrs["type"] == "primary":
            if not attrs.get("email"):
                raise serializers.ValidationError(detail="email_required", code="email")

        return attrs
