from django.db.models import Model
from rest_framework.serializers import EmailField, Serializer, UUIDField


class CreateUsersBulkSerializer(Serializer[Model]):
    email = EmailField(read_only=True)
    auth_id = UUIDField(read_only=True)
