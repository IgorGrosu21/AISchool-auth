from rest_framework import serializers

from api.models import User

from ..fields import CodeField, EmailField, PasswordField


class VerifyCodeSerializer(serializers.Serializer[User]):
    email = EmailField(write_only=True)
    code = CodeField(write_only=True)
    purpose = serializers.ChoiceField(choices=["verify_email", "restore_password"])
    password = PasswordField(write_only=True)
    remember_me = serializers.BooleanField(default=False, write_only=True)
