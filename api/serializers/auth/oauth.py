from rest_framework import serializers

from api.models import User

from ..fields import EmailField


class OAuth2Serializer(serializers.Serializer[User]):
    email = EmailField(write_only=True)
    token = serializers.CharField(write_only=True)
    provider = serializers.ChoiceField(choices=["google", "facebook"])
