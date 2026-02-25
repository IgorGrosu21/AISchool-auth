from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from shared_backend.utils.exceptions import Forbidden, NotFound, Unauthorized, errors

from services.models import Client
from services.serializers import ServiceTokenSerializer
from utils.jwt import create_service_token

from .base import BaseProducerView


@extend_schema(
    tags=["service - producers"],
    summary="Auth",
    description="Auth a service",
    request=ServiceTokenSerializer,
    responses={
        201: ServiceTokenSerializer,
        **errors(Forbidden, NotFound, Unauthorized),
    },
)
class AuthView(BaseProducerView[ServiceTokenSerializer]):
    serializer_class = ServiceTokenSerializer
    authentication_classes = []
    permission_classes = []

    def process_request(
        self, request: Request, serializer: ServiceTokenSerializer | None = None
    ) -> ServiceTokenSerializer | None:
        if not serializer:
            return None

        id = serializer.validated_data["id"]
        secret = serializer.validated_data["secret"]

        service = Client.get_service(id)
        if not service:
            raise NotFound(detail="service_not_found", attr="id")

        # Verify service secret
        if not service.compare_secret(secret):
            raise Unauthorized(detail="invalid_service_credentials", attr="secret")

        # Check if service is allowed to access the API
        original_host: str = self.request.get_host()
        if not service.compare_host(original_host):
            raise Forbidden(detail="service_not_allowed", attr="host")

        # Generate service token
        access_token = create_service_token(id)

        serializer.set_access_token(access_token)
        return serializer
