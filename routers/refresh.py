from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from sqlalchemy.orm import Session
from schemas.schemas import RefreshTokenRequest, AccessTokenResponse
from utils.jwt_utils import verify_refresh_token, create_access_token
from core.settings import ACCESS_TOKEN_EXPIRE
from core.database import get_db
from utils.token_storage import token_blacklist
from core.dependencies import get_current_user
from models.models import User

router = APIRouter(tags=["refresh"])

@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token using refresh token"""
    if not request.refresh:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="no_refresh_token"
        )

    try:
        # Verify refresh token and get email and jti
        token_data = verify_refresh_token(request.refresh)
        email = token_data["email"]
        jti = token_data.get("jti")

        # Check if token is blacklisted
        if token_blacklist.is_blacklisted(db, request.refresh, jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid_refresh_token"
            )

        # Create new access token
        access_token = create_access_token(
            {"sub": email},
            expires_delta=ACCESS_TOKEN_EXPIRE
        )

        return AccessTokenResponse(access=access_token)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid_refresh_token"
        ) from e

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: RefreshTokenRequest,
    _current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout by blacklisting refresh token"""
    if not request.refresh:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="no_refresh_token"
        )

    try:
        # Verify token and get expiry and user info
        from jose import jwt
        from utils.jwt_utils import _get_public_key_from_jwks

        # Get kid from token header
        unverified = jwt.get_unverified_header(request.refresh)
        kid = unverified.get("kid")

        if kid:
            # Get public key for decoding
            public_key = _get_public_key_from_jwks(kid)
            payload = jwt.decode(request.refresh, public_key, algorithms=["RS256"])
            exp = datetime.fromtimestamp(payload.get("exp", 0))
            user_email = payload.get("sub")
            jti = payload.get("jti")

            # Add to blacklist
            if user_email:
                token_blacklist.add(db, request.refresh, exp, user_email, jti)
    except Exception:
        # Even if token is invalid, return success
        pass

    return None

@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout from all devices (blacklist all user tokens)"""
    token_blacklist.clear_user_tokens(db, current_user.email)
    return None
