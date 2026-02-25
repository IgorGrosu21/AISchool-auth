from rest_framework import serializers

from api.models import User


class UserSerializer(serializers.Serializer[User]):
    email = serializers.EmailField(read_only=True)
    backup_email = serializers.EmailField(read_only=True)
