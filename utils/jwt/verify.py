from datetime import datetime, timezone

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from jose import JWTError, jwt

from core import ALGORITHM, VERIFICATION_SECRET, get_key_manager
from schemas import BadRequest, Unauthorized

def _get_public_key_from_jwks(kid: str):
    """Get public key from JWKS for verification (only non-expired keys)"""
    manager = get_key_manager()
    now = datetime.now()

    # Find key by kid
    key_data = None
    for k in manager.keys.get("keys", []):
        if k["kid"] == kid:
            key_data = k
            break

    if not key_data:
        raise Unauthorized.exception(detail="token_key_not_found", attr="token")

    # Check if key is expired
    expires_at = datetime.fromisoformat(key_data["expires_at"])
    if expires_at < now:
        raise Unauthorized.exception(detail="token_key_expired", attr="token")

    # Load public key
    public_key = serialization.load_pem_public_key(
        key_data["public_key"].encode('utf-8'),
        backend=default_backend()
    )

    return public_key

def verify_token(token: str, token_type: str):
    """Verify and decode JWT token using RS256"""
    try:
        # Decode without verification first to get kid
        unverified = jwt.get_unverified_header(token)
        kid = unverified.get("kid")

        if not kid:
            raise Unauthorized.exception(detail="token_missing_key_id", attr="token")

        # Get public key for verification
        public_key = _get_public_key_from_jwks(kid)

        # Verify and decode token
        payload = jwt.decode(token, public_key, algorithms=[ALGORITHM])

        if payload.get("type") != token_type:
            raise Unauthorized.exception(detail="invalid_token_type", attr="token")

        email: str | None = payload.get("email")
        if email is None:
            raise Unauthorized.exception(detail="invalid_token_payload", attr="token")
        jti: str = payload.get("jti")
        exp_timestamp = payload.get("exp", 0)
        exp: datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        return {"email": email, "jti": jti, "exp": exp}
    except JWTError as exc:
        raise Unauthorized.exception(detail="invalid_credentials", attr="token") from exc
    except Unauthorized.exception:
        raise
    except Exception as exc:
        raise Unauthorized.exception(detail="invalid_credentials", attr="token") from exc

def verify_refresh_token(token: str):
    """Verify refresh token"""
    return verify_token(token, token_type="refresh")

def verify_access_token(token: str):
    """Verify access token"""
    return verify_token(token, token_type="access")

def verify_verification_token(token: str) -> str:
    """Verify and decode JWT verification token"""
    try:
        payload = jwt.decode(
            token,
            VERIFICATION_SECRET,
            algorithms=["HS256"],
            options={"verify_exp": True}
        )

        # Verify token type
        email = payload.get("email")
        if payload.get("type") == "email_verification" and email:
            return email

        raise BadRequest.exception(detail="invalid_or_expired_token", attr="token")

    except Exception as exc:
        raise BadRequest.exception(detail="invalid_or_expired_token", attr="token") from exc