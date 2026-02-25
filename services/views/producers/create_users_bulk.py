from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from api.models import User
from api.serializers import SignupSerializer
from services.serializers import CreateUsersBulkSerializer

from .base import BaseProducerView


@extend_schema(
    tags=["service - producers"],
    summary="Create users bulk",
    description="Create users bulk",
    request=SignupSerializer(many=True),
    responses={201: CreateUsersBulkSerializer},
)
class CreateUsersBulkView(BaseProducerView[CreateUsersBulkSerializer]):
    def post(self, request: Request) -> Response:
        serializer = SignupSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        emails = [user["email"] for user in serializer.validated_data]

        existing_users = User.objects.filter(Q(email__in=emails) | Q(backup_email__in=emails))

        if existing_users.count() > 0:
            return Response(
                [
                    {
                        "email": user.email,
                        "auth_id": "",
                    }
                    for user in existing_users
                ],
                status=status.HTTP_200_OK,
            )

        users = []
        for user_data in serializer.validated_data:
            user = User(email=user_data["email"])
            user.set_password(user_data["password"])
            users.append(user)

        users = User.objects.bulk_create(users)

        return Response(
            [
                {
                    "email": user.email,
                    "auth_id": str(user.id),
                }
                for user in users
            ],
            status=status.HTTP_201_CREATED,
        )
