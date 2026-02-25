from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from shared_backend.utils.exceptions import BadRequest, errors

from api.models import RefreshToken
from api.serializers import RefreshTokenSerializer, TokensSerializer
from utils.jwt import verify_refresh_token

from ..helpers import create_failed_login_event, create_tokens_for_user


@extend_schema(
    tags=["api - token"],
    summary="Refresh",
    description="Refresh tokens (rotating refresh token)",
    request=RefreshTokenSerializer,
    responses={
        200: TokensSerializer,
        **errors(BadRequest),
    },
)
@api_view(["POST"])
def refresh_token_view(request: Request) -> Response:
    serializer = RefreshTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    refresh_token_str = serializer.validated_data["refresh"]

    token_data = verify_refresh_token(refresh_token_str)
    auth_id = token_data.get("auth_id")
    jti = token_data.get("jti")

    try:
        refresh_token_obj: RefreshToken = RefreshToken.objects.select_related(
            "chain", "chain__user", "chain__login_event"
        ).get(jti=jti)
    except RefreshToken.DoesNotExist as e:
        raise BadRequest(detail="invalid_refresh_token", attr="refresh") from e

    if str(refresh_token_obj.chain.user.id) != auth_id:
        raise BadRequest(detail="invalid_refresh_token", attr="refresh")

    if refresh_token_obj.is_expired():
        refresh_token_obj.chain.delete_tokens(refresh_token_obj.expires_at)
        raise BadRequest(detail="refresh_token_expired", attr="refresh")

    if refresh_token_obj.is_revoked:
        refresh_token_obj.chain.revoke()
        create_failed_login_event(
            refresh_token_obj.chain.user,
            request,
            login_method="refresh",
            failure_reason="revoked_token_used",
        )
        raise BadRequest(detail="revoked_token_used", attr="refresh")

    if len(refresh_token_obj.chain) >= 30:
        refresh_token_obj.chain.revoke()
        create_failed_login_event(
            refresh_token_obj.chain.user,
            request,
            login_method="refresh",
            failure_reason="token_rotation_limit_reached",
        )
        raise BadRequest(detail="token_rotation_limit_reached", attr="refresh")

    latest_token = refresh_token_obj.chain.active_token()

    if latest_token is None:
        refresh_token_obj.chain.revoke()
        create_failed_login_event(
            refresh_token_obj.chain.user,
            request,
            login_method="refresh",
            failure_reason="chain_state_inconsistent",
        )
        raise BadRequest(detail="chain_state_inconsistent", attr="refresh")

    if latest_token.jti != refresh_token_obj.jti:
        refresh_token_obj.chain.revoke()
        create_failed_login_event(
            refresh_token_obj.chain.user,
            request,
            login_method="refresh",
            failure_reason="token_reuse_detected",
        )
        raise BadRequest(detail="token_reuse_detected", attr="refresh")

    # All checks passed - proceed with token rotation
    try:
        with transaction.atomic():
            tokens = create_tokens_for_user(
                auth_id=auth_id,
                request_info={"request": request, "login_method": "refresh"},
                remember_me=refresh_token_obj.chain.remember_me,
                chain=refresh_token_obj.chain,
            )

            if refresh_token_obj.chain.login_event:
                refresh_token_obj.chain.login_event.last_activity = timezone.now()
                refresh_token_obj.chain.login_event.save()

        return Response(TokensSerializer(tokens).data, status=status.HTTP_200_OK)
    except Exception as e:
        raise BadRequest(detail="invalid_refresh_token", attr="refresh") from e
