from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from shared_backend.utils.exceptions import Unauthorized, errors

from api.models import RefreshToken
from api.serializers import RefreshTokenSerializer
from utils.jwt import verify_refresh_token
from utils.jwt.authentification.user import JWTUserAuthentication


@extend_schema(
    tags=["api - token"],
    summary="Logout",
    description="Logout a user",
    request=RefreshTokenSerializer,
    responses={
        204: None,
        **errors(Unauthorized),
    },
)
@api_view(["POST"])
@authentication_classes([JWTUserAuthentication])
@permission_classes([IsAuthenticated])
def logout_view(request: Request) -> Response:
    serializer = RefreshTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    refresh_token_str = serializer.validated_data["refresh"]

    if not refresh_token_str:
        return Response(status=status.HTTP_204_NO_CONTENT)

    try:
        token_data = verify_refresh_token(refresh_token_str)
        jti = token_data.get("jti")

        if jti:
            # Delete the chain (manual logout)
            try:
                refresh_token: RefreshToken = RefreshToken.objects.get(jti=jti)
                refresh_token.chain.delete()
            except RefreshToken.DoesNotExist:
                pass
    except Exception:
        pass

    return Response(status=status.HTTP_204_NO_CONTENT)
