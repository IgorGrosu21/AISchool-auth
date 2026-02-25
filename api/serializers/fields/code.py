from rest_framework import serializers


class CodeField(serializers.CharField):
    def validate(self, value: str) -> str:
        if not value:
            raise serializers.ValidationError(detail="code_required", code="code")

        normalized = value.strip().upper()
        if len(normalized) != 6 or not normalized.isalnum():
            raise serializers.ValidationError(detail="invalid_verification_code", code="code")

        return normalized
