from typing import cast

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from shared_backend.utils.exceptions import BadRequest, errors

from api.models import User
from api.serializers import UserPasswordSerializer


@extend_schema(
    tags=["api - user"],
    summary="Update Password",
    description="Update the password for a user",
    request=UserPasswordSerializer,
    responses={
        204: None,
        **errors(BadRequest),
    },
)
@api_view(["POST"])
def user_password_view(request: Request) -> Response:
    serializer = UserPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    password = serializer.validated_data["password"]
    user: User = cast(User, request.user)

    if user.check_password(password):
        raise BadRequest(detail="password_the_same", attr="password")

    user.set_password(password)
    user.save()
    return Response(None, status=status.HTTP_204_NO_CONTENT)
