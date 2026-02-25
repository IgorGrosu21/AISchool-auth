from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from shared_backend.utils.exceptions import BadRequest, errors

from services.serializers import GenerateTokenSerializer
from utils.jwt import generate_token

from .base import BaseProducerView


@extend_schema(
    tags=["service - producers"],
    summary="Generate Token",
    description="Generate a token or tokens for a service",
    request=GenerateTokenSerializer,
    responses={
        201: GenerateTokenSerializer,
        **errors(BadRequest),
    },
)
class GenerateTokenView(BaseProducerView[GenerateTokenSerializer]):
    serializer_class = GenerateTokenSerializer

    def process_request(
        self, request: Request, serializer: GenerateTokenSerializer | None = None
    ) -> GenerateTokenSerializer | None:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        token_type: str = serializer.validated_data.get("token_type", None)
        if not token_type:
            raise BadRequest(detail="token_type_required", attr="token_type")

        sub = serializer.validated_data.get("sub", None)
        subs = serializer.validated_data.get("subs", None)
        if not sub and not subs:
            raise BadRequest(detail="sub_or_subs_required", attr="sub_or_subs")

        # generate_token expects data dict, token_type, and expires_in timedelta
        if sub:
            token = generate_token(data=sub, token_type=token_type)
            serializer.set_token(token)
        elif subs:
            tokens = [generate_token(data=sub, token_type=token_type) for sub in subs]
            serializer.set_tokens(tokens)
        return serializer
