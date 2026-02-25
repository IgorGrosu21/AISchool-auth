from typing import Any, TypedDict

from api.models import Chain, LoginEvent, RefreshToken, User
from utils.jwt import create_auth_tokens

from .request_metadata import get_login_metadata


class UserTokens(TypedDict):
    access: str
    refresh: str
    long_refresh: bool


def create_tokens_for_user(
    auth_id: str, request_info: dict[str, Any], remember_me: bool, chain: Chain | None = None
) -> UserTokens:
    """Create both access and refresh tokens for a user with chain tracking."""
    tokens = create_auth_tokens(auth_id, long_refresh=remember_me)
    access_token = tokens["access"]
    refresh_token, expire, jti = tokens["refresh"]

    if not chain:
        user = User.objects.get(id=auth_id)
        metadata = get_login_metadata(**request_info)
        login_event = LoginEvent.objects.create(user=user, **metadata)

        chain = Chain.objects.create(user=user, login_event=login_event, remember_me=remember_me)

    RefreshToken.objects.create(jti=jti, expires_at=expire, chain=chain)

    return {"access": access_token, "refresh": refresh_token, "long_refresh": remember_me}
