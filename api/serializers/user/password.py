from rest_framework import serializers

from api.models import User


class UserPasswordSerializer(serializers.Serializer[User]):
    password = serializers.CharField(write_only=True)
