from rest_framework import serializers

from .tokens import UserTokens


class AccessTokenSerializer(serializers.Serializer[UserTokens]):
    access = serializers.CharField(read_only=True)
