from datetime import UTC, datetime
from typing import Any

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from django.conf import settings
from jose import JWTError, jwt
from shared_backend.utils.exceptions import BadRequest

from .rsa_keys import get_public_key


def _get_public_key_from_jwks(kid: str) -> PublicKeyTypes:
    """Get public key from JWKS for verification

    Allows verification with expired keys (as long as not retired)
    Keys are kept available for verification until retires_at (30 days)
    """
    public_key = get_public_key(kid)
    return serialization.load_pem_public_key(public_key, backend=default_backend())


def verify_token(token: str, token_type: str) -> dict[str, Any]:
    """Verify and decode JWT token using RS256"""
    try:
        # Decode without verification first to get kid
        unverified = jwt.get_unverified_header(token)
        kid = unverified.get("kid")

        if not kid:
            raise BadRequest(detail="token_missing_key_id", attr="token")

        # Get public key for verification
        public_key = _get_public_key_from_jwks(kid)

        # Verify and decode token
        payload = jwt.decode(token, public_key, algorithms=[settings.ALGORITHM])  # type: ignore

        if not payload.get("type", "").startswith(token_type):
            raise BadRequest(detail="invalid_token_type", attr="token")

        result: dict[str, Any] = {
            "type": token_type,
        }

        # Handle different token types
        if token_type == "service":
            # Service tokens have service_id
            service_id = payload.get("service_id")
            if service_id is None:
                raise BadRequest(detail="invalid_token_payload", attr="token")
            result["service_id"] = service_id
        else:
            # User tokens (access, refresh)
            auth_id = payload.get("auth_id")
            if auth_id is None:
                raise BadRequest(detail="invalid_token_payload", attr="token")
            result["auth_id"] = auth_id

            # Refresh tokens have jti
            jti = payload.get("jti")
            if jti:
                result["jti"] = jti

        exp_timestamp = payload.get("exp", 0)
        exp = datetime.fromtimestamp(exp_timestamp, tz=UTC)
        result["exp"] = exp

        return result
    except JWTError as exc:
        raise BadRequest(detail="invalid_credentials", attr="token") from exc
    except BadRequest:
        raise
    except Exception as exc:
        raise BadRequest(detail="invalid_credentials", attr="token") from exc


def verify_access_token(token: str) -> dict[str, Any]:
    """Verify access token"""
    return verify_token(token, token_type="access")


def verify_refresh_token(token: str) -> dict[str, Any]:
    """Verify refresh token"""
    return verify_token(token, token_type="refresh")


def verify_service_token(token: str) -> dict[str, Any]:
    """Verify service token"""
    return verify_token(token, token_type="service")
