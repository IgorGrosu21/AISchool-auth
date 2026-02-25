from typing import cast

from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from shared_backend.utils.exceptions import BadRequest, errors

from api.models import User, VerificationCode
from api.serializers import UserEmailSerializer, VerificationRequiredSerializer
from services.models import Client
from services.views import SendVerificationEmailView


@extend_schema(
    tags=["api - user"],
    summary="Update Email",
    description="Update the email for a user",
    request=UserEmailSerializer,
    responses={
        200: VerificationRequiredSerializer,
        204: None,
        **errors(BadRequest),
    },
)
@api_view(["POST"])
def user_email_view(request: Request) -> Response:
    serializer = UserEmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user: User = cast(User, request.user)
    email = serializer.validated_data["email"]
    type = serializer.validated_data["type"]

    if type == "backup" and not email:
        user.backup_email = email
        user.save()
        return Response(None, status=status.HTTP_204_NO_CONTENT)

    # Check if email is the same as the current email
    email_type = "email" if type == "primary" else "backup_email"
    existing_email: str | None = getattr(user, email_type)
    if email == existing_email:
        raise BadRequest(detail="email_the_same", attr=email_type)

    # Check if user already exists
    if User.objects.filter(Q(email=email) | Q(backup_email=email)).exists():
        raise BadRequest(detail="email_already_exists", attr=email_type)

    code = serializer.validated_data["code"]

    purpose = f"verify_{email_type}"
    if not code:
        verification_code = VerificationCode.create(user=user, purpose=purpose)
        verification_code.save()
        Client.call_consumer(
            SendVerificationEmailView,
            {
                "email": email,
                "code": verification_code.code,
                "purpose": "verify_email",
            },
            user,
            request.language,  # type: ignore[attr-defined]
        )
        return Response({"purpose": purpose}, status=status.HTTP_200_OK)

    verification_codes = VerificationCode.objects.filter(
        user=user, code=code.upper(), purpose=purpose
    )
    if not verification_codes.exists():
        raise BadRequest(detail="invalid_code", attr="code")

    verification_codes.delete()
    if type == "primary":
        user.email = email
    else:
        user.backup_email = email
    user.save()
    return Response(None, status=status.HTTP_204_NO_CONTENT)
