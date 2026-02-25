from rest_framework import serializers

from api.models import User


class VerificationRequiredSerializer(serializers.Serializer[User]):
    purpose = serializers.ChoiceField(choices=["verify_email", "restore_password"])
