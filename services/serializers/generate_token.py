from django.db.models import Model
from rest_framework import serializers


class GenerateTokenSerializer(serializers.Serializer[Model]):
    token_type = serializers.CharField(required=True, write_only=True)
    sub = serializers.DictField(required=False, write_only=True)
    subs = serializers.ListField(child=serializers.DictField(), required=False, write_only=True)
    token = serializers.SerializerMethodField()
    tokens = serializers.SerializerMethodField()

    def get_token(self, _: Model) -> str | None:
        return self._token if hasattr(self, "_token") else None

    def set_token(self, value: str) -> None:
        self._token = value

    def get_tokens(self, _: Model) -> list[str] | None:
        return self._tokens if hasattr(self, "_tokens") else None

    def set_tokens(self, value: list[str]) -> None:
        self._tokens = value
