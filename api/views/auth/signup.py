from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from shared_backend.utils.exceptions import BadRequest, errors

from api.models import User, VerificationCode
from api.serializers import SignupSerializer, VerificationRequiredSerializer
from services.models import Client
from services.views import SendVerificationEmailView


@extend_schema(
    tags=["api - auth"],
    summary="Signup",
    description="Signup a new user",
    request=SignupSerializer,
    responses={
        200: VerificationRequiredSerializer,
        **errors(BadRequest),
    },
)
@api_view(["POST"])
def signup_view(request: Request) -> Response:
    serializer = SignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data["email"]
    password = serializer.validated_data["password"]

    # Check if user already exists
    if User.objects.filter(Q(email=email) | Q(backup_email=email)).exists():
        raise BadRequest(detail="email_already_exists", attr="email")

    # Create user
    user: User = User.objects.create(email=email)
    user.set_password(password)
    user.save()

    # Issue verification code and send email
    verification_code = VerificationCode.create(user=user, purpose="verify_email")
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

    return Response({"purpose": "verify_email"}, status=status.HTTP_200_OK)
