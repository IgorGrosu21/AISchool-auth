from typing import cast

from drf_spectacular.utils import extend_schema
from rest_framework.generics import DestroyAPIView, RetrieveAPIView

from api.models import User
from api.serializers import UserSerializer


@extend_schema(
    tags=["api - user"],
    summary="Get User",
    description="Get the user",
    responses={
        200: UserSerializer,
    },
)
class UserView(RetrieveAPIView[User], DestroyAPIView[User]):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_object(self) -> User:
        return cast(User, self.request.user)
