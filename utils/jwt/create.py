import secrets
from datetime import datetime
from typing import Any, TypedDict

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from django.conf import settings
from django.utils import timezone
from jose import jwt

from .rsa_keys import get_current_kid, get_private_key


def _generate_jti() -> str:
    """Generate a unique JWT ID"""
    return secrets.token_urlsafe(32)


def _get_signing_key(kid: str) -> bytes:
    """Get private key for signing tokens"""
    if not kid:
        kid = get_current_kid()
    return get_private_key(kid)


def _create_signed_token(
    data: dict[str, Any], token_type: str, kid: str | None = None
) -> tuple[str, datetime]:
    """Create JWT token signed with RS256"""
    now = timezone.now()

    expire_map = {
        "access": settings.ACCESS_TOKEN_EXPIRE,
        "refresh_short": settings.REFRESH_TOKEN_EXPIRE_SHORT,
        "refresh_long": settings.REFRESH_TOKEN_EXPIRE_LONG,
        "service": settings.SERVICE_TOKEN_EXPIRE,
    }

    expire = now + expire_map.get(token_type, settings.ACCESS_TOKEN_EXPIRE)

    to_encode = data.copy()
    # Convert datetime to Unix timestamp (seconds since epoch) for JWT standard
    to_encode.update(
        {"exp": int(expire.timestamp()), "type": token_type, "iat": int(now.timestamp())}
    )

    # Add kid to header if not provided
    if not kid:
        kid = get_current_kid()

    # Get private key
    private_key_pem = _get_signing_key(kid)
    private_key = serialization.load_pem_private_key(
        private_key_pem, password=None, backend=default_backend()
    )

    # Encode token with RS256
    headers = {"kid": kid}
    encoded_jwt = jwt.encode(
        to_encode,
        private_key,  # type: ignore
        algorithm=settings.ALGORITHM,
        headers=headers,
    )
    return encoded_jwt, expire


def create_access_token(data: dict[str, Any], kid: str | None = None) -> str:
    """Create JWT access token signed with RS256"""
    token, _ = _create_signed_token(data, "access", kid=kid)
    return token


def create_refresh_token(
    data: dict[str, Any], long_refresh: bool = False, kid: str | None = None
) -> tuple[str, datetime, str]:
    """Create JWT refresh token with optional JTI, signed with RS256"""
    jti = _generate_jti()
    token_type = "refresh_short" if not long_refresh else "refresh_long"
    token, expire = _create_signed_token({**data, "jti": jti}, token_type, kid=kid)
    return token, expire, jti


class AuthTokens(TypedDict):
    access: str
    refresh: tuple[str, datetime, str]


def create_auth_tokens(auth_id: str, long_refresh: bool = False) -> AuthTokens:
    """Create JWT auth tokens for a user"""
    kid = get_current_kid()
    access_token = create_access_token({"auth_id": auth_id}, kid)
    refresh_token, expire, jti = create_refresh_token({"auth_id": auth_id}, long_refresh, kid)
    return {"access": access_token, "refresh": (refresh_token, expire, jti)}


def create_service_token(service_id: str) -> str:
    """Create JWT service token signed with RS256"""
    token, _ = _create_signed_token({"service_id": service_id}, "service")
    return token


def generate_token(data: dict[str, Any], token_type: str) -> str:
    token, _ = _create_signed_token(data, token_type)
    return token
