from typing import cast

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from shared_backend.utils.exceptions import BadRequest, errors

from api.models import User
from api.serializers import OAuth2Serializer, TokensSerializer

from ..helpers import (
    create_failed_login_event,
    create_tokens_for_user,
    validate_oauth2_token,
)


@extend_schema(
    tags=["api - auth"],
    summary="OAuth2",
    description="OAuth2 login",
    request=OAuth2Serializer,
    responses={
        201: TokensSerializer,
        **errors(BadRequest),
    },
)
@api_view(["POST"])
def oauth2_view(request: Request) -> Response:
    serializer = OAuth2Serializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data["email"]
    token = serializer.validated_data["token"]
    provider = serializer.validated_data["provider"]

    # Validate OAuth2 token
    try:
        verified_email = validate_oauth2_token(provider, token, email)
    except BadRequest as e:
        try:
            user = User.objects.get(email=email)
            create_failed_login_event(
                user, request, login_method=provider, failure_reason=cast(str, e.detail)
            )
        except User.DoesNotExist:
            pass
        raise e

    # Get or create user
    user, created = User.objects.get_or_create(email=verified_email, defaults={"is_verified": True})

    if not created:
        user.is_verified = True
        user.save()

    # Create tokens
    tokens = create_tokens_for_user(
        auth_id=str(user.id),
        request_info={"request": request, "login_method": provider},
        remember_me=True,
    )
    return Response(TokensSerializer(tokens).data, status=status.HTTP_201_CREATED)
