from datetime import datetime, timezone
import secrets
from typing import Optional

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from jose import jwt

from core import (
    ACCESS_TOKEN_EXPIRE,
    REFRESH_TOKEN_EXPIRE,
    VERIFICATION_TOKEN_EXPIRE,
    VERIFICATION_SECRET,
    ALGORITHM,
    get_current_kid,
    get_private_key,
)

from models import create_or_update_refresh_token


def _generate_jti() -> str:
    """Generate a unique JWT ID"""
    return secrets.token_urlsafe(32)


def _get_signing_key(kid: Optional[str] = None) -> bytes:
    """Get private key for signing tokens"""
    if not kid:
        kid = get_current_kid()
    return get_private_key(kid)


def _create_signed_token(data: dict, token_type: str, kid: Optional[str] = None):
    """Create JWT token signed with RS256"""
    expire_map = {
        "access": ACCESS_TOKEN_EXPIRE,
        "refresh": REFRESH_TOKEN_EXPIRE,
    }

    now = datetime.now(timezone.utc)
    expire = now + expire_map[token_type]

    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": token_type, "iat": now})

    # Add kid to header if not provided
    if not kid:
        kid = get_current_kid()

    # Get private key
    private_key_pem = _get_signing_key(kid)
    private_key = serialization.load_pem_private_key(
        private_key_pem,
        password=None,
        backend=default_backend()
    )

    # Encode token with RS256
    headers = {"kid": kid}
    encoded_jwt = jwt.encode(to_encode, private_key, algorithm=ALGORITHM, headers=headers)
    return encoded_jwt, expire


def create_access_token(data: dict, kid: Optional[str] = None):
    """Create JWT access token signed with RS256"""
    token, _ = _create_signed_token(data, "access", kid)
    return token


def create_refresh_token(data: dict, kid: Optional[str] = None):
    """Create JWT refresh token with optional JTI, signed with RS256"""
    token, expire = _create_signed_token(data, "refresh", kid)
    return token, expire


def create_tokens_for_user(email: str, db=None):
    """Create both access and refresh tokens for a user"""
    kid = get_current_kid()
    access_token = create_access_token({"email": email}, kid=kid)

    # Generate JTI for refresh token
    jti = _generate_jti()
    refresh_token, expire = create_refresh_token({"email": email, "jti": jti}, kid=kid)

    # If database session is provided, create token record
    if db:
        create_or_update_refresh_token(db, {
            "user_email": email,
            "expires_at": expire,
            "jti": jti,
            "is_blacklisted": False,
        })

    return {
        "access": access_token,
        "refresh": refresh_token
    }


def create_verification_token(user_email: str) -> str:
    """Generate a stateless JWT verification token"""
    now = datetime.now(timezone.utc)
    token = jwt.encode({
        "email": user_email,
        "type": "email_verification",
        "exp": now + VERIFICATION_TOKEN_EXPIRE,
        "iat": now,
    }, VERIFICATION_SECRET, algorithm="HS256")
    return token
