from rest_framework import serializers

from api.models import User

from ..fields import EmailField, PasswordField


class LoginSerializer(serializers.Serializer[User]):
    email = EmailField(write_only=True)
    password = PasswordField(write_only=True)
    remember_me = serializers.BooleanField(default=False, write_only=True)
