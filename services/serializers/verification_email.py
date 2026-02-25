from rest_framework import serializers

from api.models import User


class VerificationEmailSerializer(serializers.Serializer[User]):
    email = serializers.CharField(required=True, write_only=True)
    code = serializers.CharField(required=True, write_only=True)
    purpose = serializers.CharField(required=True, write_only=True)
