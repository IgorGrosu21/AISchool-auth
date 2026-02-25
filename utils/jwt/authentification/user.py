from typing import Any

from shared_backend.utils.exceptions import NotFound
from shared_backend.utils.jwt_authentification import (
    JWTUserAuthentication as BaseJWTUserAuthentication,
)

from api.models import User

from ..verify import verify_access_token


class JWTUserAuthentication(BaseJWTUserAuthentication):
    token_type = "access"

    def decode_token(self, token: str) -> dict[str, Any]:
        return verify_access_token(token)

    def serialize_payload(self, payload: dict[str, Any]) -> User:
        try:
            auth_id: str = payload.get("auth_id", "")
            instance = User.objects.get(id=auth_id)
        except User.DoesNotExist as e:
            raise NotFound(detail="User not found", attr="auth_id") from e
        return instance
