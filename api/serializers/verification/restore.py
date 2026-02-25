from rest_framework import serializers

from api.models import User

from ..fields import CodeField, EmailField, PasswordField


class RestorePasswordSerializer(serializers.Serializer[User]):
    email = EmailField(write_only=True)
    password = PasswordField(write_only=True)
    code = CodeField(write_only=True, required=False)
