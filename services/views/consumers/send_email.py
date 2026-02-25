from rest_framework.request import Request
from shared_backend.services.views import BaseConsumerView

from services.models import Client
from services.serializers import VerificationEmailSerializer
from utils.jwt.authentification.user import JWTUserAuthentication


class SendVerificationEmailView(BaseConsumerView):
    authentication_classes = [JWTUserAuthentication]
    producer_service_id = "notifications-service"
    producer_url = "send-auth-email"
    client = Client

    def get_data(self, request: Request) -> dict[str, str]:
        serializer = VerificationEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return {
            "email": serializer.validated_data["email"],
            "code": serializer.validated_data["code"],
            "purpose": serializer.validated_data["purpose"],
        }
