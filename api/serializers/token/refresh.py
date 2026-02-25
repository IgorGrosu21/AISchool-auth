from rest_framework import serializers

from .tokens import UserTokens


class RefreshTokenSerializer(serializers.Serializer[UserTokens]):
    refresh = serializers.CharField(write_only=True)
