from django.db.models import Model
from rest_framework import serializers


class ServiceTokenSerializer(serializers.Serializer[Model]):
    id = serializers.CharField(required=True, write_only=True)
    secret = serializers.CharField(required=True, write_only=True)
    access_token = serializers.SerializerMethodField()

    def get_access_token(self, _: Model) -> str:
        return self._access_token

    def set_access_token(self, value: str) -> None:
        self._access_token = value
