from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from shared_backend.utils.exceptions import BadRequest, NotFound, errors

from api.models import User, VerificationCode
from api.serializers import RestorePasswordSerializer, VerificationRequiredSerializer
from services.models import Client
from services.views import SendVerificationEmailView


@extend_schema(
    tags=["api - verification"],
    summary="Restore Password",
    description="Restore a user's password",
    request=RestorePasswordSerializer,
    responses={
        200: VerificationRequiredSerializer,
        **errors(BadRequest, NotFound),
    },
)
@api_view(["POST"])
def restore_password_view(request: Request) -> Response:
    serializer = RestorePasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data["email"]
    password = serializer.validated_data["password"]

    try:
        user: User = User.objects.get(email=email)
    except User.DoesNotExist as e:
        raise NotFound(detail="email_not_found", attr="email") from e

    if user.check_password(password):
        raise BadRequest(detail="password_the_same", attr="password")

    # Create verification code
    verification_code = VerificationCode.create(user=user, purpose="password_reset")
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

    return Response({"purpose": "password_reset"}, status=status.HTTP_200_OK)
