from datetime import datetime, timedelta, timezone
import secrets
from typing import Dict, Optional

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from fastapi import HTTPException, status
from jose import JWTError, jwt

from core.rsa_keys import get_current_kid, get_key_manager, get_private_key
from core.settings import ALGORITHM, ACCESS_TOKEN_EXPIRE, REFRESH_TOKEN_EXPIRE

def generate_jti() -> str:
    """Generate a unique JWT ID"""
    return secrets.token_urlsafe(32)

def _get_signing_key(kid: Optional[str] = None) -> bytes:
    """Get private key for signing tokens"""
    if not kid:
        kid = get_current_kid()
    return get_private_key(kid)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, kid: Optional[str] = None):
    """Create JWT access token signed with RS256"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + ACCESS_TOKEN_EXPIRE

    # Add kid to header if not provided
    if not kid:
        kid = get_current_kid()

    to_encode.update({"exp": expire, "type": "access"})

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
    return encoded_jwt

def create_refresh_token(data: dict, jti: Optional[str] = None, kid: Optional[str] = None):
    """Create JWT refresh token with optional JTI, signed with RS256"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + REFRESH_TOKEN_EXPIRE

    # Add JTI if provided
    if jti:
        to_encode["jti"] = jti

    # Add kid to header if not provided
    if not kid:
        kid = get_current_kid()

    to_encode.update({"exp": expire, "type": "refresh"})

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
    return encoded_jwt

def create_tokens_for_user(email: str, db=None):
    """Create both access and refresh tokens for a user"""
    kid = get_current_kid()
    access_token = create_access_token({"sub": email}, kid=kid)

    # Generate JTI for refresh token
    jti = generate_jti()
    refresh_token = create_refresh_token({"sub": email}, jti=jti, kid=kid)

    # If database session is provided, create token record
    if db:
        from utils.token_storage import token_blacklist
        expire = datetime.now(timezone.utc) + REFRESH_TOKEN_EXPIRE
        token_blacklist.create_token_record(db, refresh_token, email, expire, jti)

    return {
        "access": access_token,
        "refresh": refresh_token
    }

def _get_public_key_from_jwks(kid: str):
    """Get public key from JWKS for verification (only non-expired keys)"""
    manager = get_key_manager()
    now = datetime.now(timezone.utc)

    # Find key by kid
    key_data = None
    for k in manager.keys.get("keys", []):
        if k["kid"] == kid:
            key_data = k
            break

    if not key_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: key not found"
        )

    # Check if key is expired
    expires_at = datetime.fromisoformat(key_data["expires_at"])
    if expires_at < now:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: key has expired"
        )

    # Load public key
    public_key = serialization.load_pem_public_key(
        key_data["public_key"].encode('utf-8'),
        backend=default_backend()
    )

    return public_key

def verify_token(token: str, token_type: str = "access"):
    """Verify and decode JWT token using RS256"""
    try:
        # Decode without verification first to get kid
        unverified = jwt.get_unverified_header(token)
        kid = unverified.get("kid")

        if not kid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing key ID"
            )

        # Get public key for verification
        public_key = _get_public_key_from_jwks(kid)

        # Verify and decode token
        payload = jwt.decode(token, public_key, algorithms=[ALGORITHM])

        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        return email
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        ) from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        ) from exc

def verify_refresh_token(token: str) -> Dict:
    """Verify refresh token and return email and jti"""
    try:
        # Decode without verification first to get kid
        unverified = jwt.get_unverified_header(token)
        kid = unverified.get("kid")

        if not kid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing key ID"
            )

        # Get public key for verification
        public_key = _get_public_key_from_jwks(kid)

        # Verify and decode token
        payload = jwt.decode(token, public_key, algorithms=[ALGORITHM])

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        email: str | None = payload.get("sub")
        jti: str = payload.get("jti")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        return {"email": email, "jti": jti}
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        ) from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        ) from exc

def verify_access_token(token: str):
    """Verify access token"""
    return verify_token(token, token_type="access")
