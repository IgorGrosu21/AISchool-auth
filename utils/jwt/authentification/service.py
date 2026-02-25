from typing import Any

from shared_backend.utils.exceptions import NotFound
from shared_backend.utils.jwt_authentification import (
    JWTServiceAuthentication as BaseJWTServiceAuthentication,
)

from services.models import Client, Service

from ..verify import verify_service_token


class JWTServiceAuthentication(BaseJWTServiceAuthentication):
    token_type = "service"

    def decode_token(self, token: str) -> dict[str, Any]:
        return verify_service_token(token)

    def serialize_payload(self, payload: dict[str, Any]) -> Service:  # type: ignore
        service_id: str = payload.get("service_id", "")
        service = Client.get_service(service_id)
        if not service:
            raise NotFound(detail="service_not_found", attr="service_id")
        return service
