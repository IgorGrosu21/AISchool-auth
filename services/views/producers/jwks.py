from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework.request import Request

from utils.jwt import get_jwks

from .base import BaseProducerView


@extend_schema(
    tags=["service - producers"],
    summary="JWKS",
    description="Get the JWKS for a service",
    request=None,
    responses={
        200: dict,
    },
)
class JWKSView(BaseProducerView[Any]):
    def get_response_data(self, request: Request, *args: Any, **kwargs: Any) -> Any:
        return {
            "keys": get_jwks(),
        }
