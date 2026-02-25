from typing import TypedDict

from rest_framework import serializers


class UserTokens(TypedDict):
    access: str
    refresh: str
    long_refresh: bool


class TokensSerializer(serializers.Serializer[UserTokens]):
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    long_refresh = serializers.BooleanField(read_only=True)
