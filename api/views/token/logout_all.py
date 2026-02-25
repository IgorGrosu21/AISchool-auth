from typing import cast

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from shared_backend.utils.exceptions import Unauthorized, errors

from api.models import Chain, User
from utils.jwt.authentification.user import JWTUserAuthentication


@extend_schema(
    tags=["api - token"],
    summary="Logout All",
    description="Logout all tokens for a user",
    request=None,
    responses={
        204: None,
        **errors(Unauthorized),
    },
)
@api_view(["POST"])
@authentication_classes([JWTUserAuthentication])
@permission_classes([IsAuthenticated])
def logout_all_view(request: Request) -> Response:
    user: User = cast(User, request.user)
    # Delete all chains for the user (cascades to all tokens)
    Chain.objects.filter(user=user).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
