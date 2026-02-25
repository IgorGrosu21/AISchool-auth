from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from shared_backend.utils.exceptions import BadRequest, NotFound, errors

from api.models import User, VerificationCode
from api.serializers import TokensSerializer, VerifyCodeSerializer

from ..helpers import create_tokens_for_user


@extend_schema(
    tags=["api - verification"],
    summary="Verify Code",
    description="Verify a verification code",
    request=VerifyCodeSerializer,
    responses={
        201: TokensSerializer,
        **errors(BadRequest, NotFound),
    },
)
@api_view(["POST"])
def verify_code_view(request: Request) -> Response:
    serializer = VerifyCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data["email"]
    code = serializer.validated_data["code"]
    purpose = serializer.validated_data["purpose"]
    password = serializer.validated_data["password"]
    remember_me = serializer.validated_data["remember_me"]

    # Find verification code
    verification_code = VerificationCode.objects.filter(
        user__email=email, purpose=purpose, code=code.upper()
    )

    if not verification_code.exists():
        raise BadRequest(detail="invalid_code", attr="code")

    # Get user
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist as e:
        raise NotFound(detail="email_not_found", attr="token") from e

    # Cleanup verification codes
    VerificationCode.objects.filter(user=user, purpose=purpose).delete()

    # Handle verification
    if purpose == "verify_email":
        user.is_verified = True
        user.save()
    elif purpose == "restore_password":
        user.set_password(password)
        user.save()

    # Create tokens
    tokens = create_tokens_for_user(
        auth_id=str(user.id),
        request_info={"request": request, "login_method": "verification"},
        remember_me=remember_me,
    )
    return Response(TokensSerializer(tokens).data, status=status.HTTP_201_CREATED)
