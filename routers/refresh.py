from fastapi import APIRouter, Depends, status
from jose import jwt
from sqlalchemy.orm import Session

from models import (
    User,
    blacklist_refresh_tokens,
    create_or_update_refresh_token,
    get_db,
    is_blacklisted,
)
from schemas import (
    AccessTokenResponse,
    BadRequest,
    RefreshTokenRequest,
    Unauthorized,
)
from utils import create_access_token, get_current_user, verify_refresh_token

router = APIRouter(tags=["refresh"])

@router.post("/refresh", response_model=AccessTokenResponse, responses={
    400: {
        "model": BadRequest.error,
        "description": "Bad request (e.g., missing or invalid refresh token)"
    },
    401: {
        "model": Unauthorized.error,
        "description": "Unauthorized (e.g., token blacklisted)"
    }
})
async def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token using refresh token"""
    if not request.refresh:
        raise BadRequest.exception(detail="no_refresh_token", attr="refresh")

    try:
        token_data = verify_refresh_token(request.refresh)
        email, jti = token_data.get("email"), token_data.get("jti")

        if is_blacklisted(db, jti):
            raise Unauthorized.exception(detail="invalid_refresh_token", attr="refresh")

        access_token = create_access_token({"email": email})

        return AccessTokenResponse(access=access_token)
    except (BadRequest.exception, Unauthorized.exception):
        raise
    except Exception as e:
        raise BadRequest.exception(detail="invalid_refresh_token", attr="refresh") from e

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Logout by blacklisting refresh token"""
    if not request.refresh:
        return None

    try:
        unverified = jwt.get_unverified_header(request.refresh)
        kid = unverified.get("kid")

        if kid:
            payload = verify_refresh_token(request.refresh)
            email, jti, exp = payload.get("email"), payload.get("jti"), payload.get("exp")
            if email and jti:
                create_or_update_refresh_token(db, {
                    "user_email": email,
                    "expires_at": exp,
                    "jti": jti,
                    "is_blacklisted": True,
                })
    except Exception:
        pass

    return None

@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Logout from all devices (blacklist all user tokens)"""
    blacklist_refresh_tokens(db, current_user.email)
    return None
