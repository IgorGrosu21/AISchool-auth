from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from shared_backend.utils.exceptions import BadRequest, NotFound, errors

from api.models import User, VerificationCode
from api.serializers import (
    LoginSerializer,
    TokensSerializer,
    VerificationRequiredSerializer,
)
from services.models import Client
from services.views import SendVerificationEmailView

from ..helpers import create_failed_login_event, create_tokens_for_user


@extend_schema(
    tags=["api - auth"],
    summary="Login",
    description="Login a user",
    request=LoginSerializer,
    responses={
        200: VerificationRequiredSerializer,
        201: TokensSerializer,
        **errors(BadRequest, NotFound),
    },
)
@api_view(["POST"])
def login_view(request: Request) -> Response:
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data["email"]
    password = serializer.validated_data["password"]
    remember_me = serializer.validated_data["remember_me"]

    try:
        user: User = User.objects.get(email=email)
    except User.DoesNotExist as e:
        # Can't track login event without a user, just raise exception
        raise NotFound(detail="email_not_found", attr="email") from e

    if not user.has_password() and user.is_verified:
        # Track failed login attempt
        create_failed_login_event(
            user, request, login_method="password", failure_reason="password_not_supported"
        )
        raise BadRequest(detail="password_not_supported", attr="password")

    if not user.check_password(password):
        # Track failed login attempt
        create_failed_login_event(
            user, request, login_method="password", failure_reason="password_incorrect"
        )
        raise BadRequest(detail="password_incorrect", attr="password")

    if not user.is_verified:
        # Issue verification code
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

    # Create tokens
    tokens = create_tokens_for_user(
        auth_id=str(user.id),
        request_info={"request": request, "login_method": "password"},
        remember_me=remember_me,
    )
    return Response(TokensSerializer(tokens).data, status=status.HTTP_201_CREATED)
