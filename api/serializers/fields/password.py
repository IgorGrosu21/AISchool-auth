from rest_framework import serializers


class PasswordField(serializers.CharField):
    def validate(self, value: str) -> str:
        if not value:
            raise serializers.ValidationError("password_required")

        if len(value) < 8:
            raise serializers.ValidationError("password_too_small")
        if value.isdigit():
            raise serializers.ValidationError("password_only_numbers")
        if value.isalpha():
            raise serializers.ValidationError("password_only_letters")

        return value
