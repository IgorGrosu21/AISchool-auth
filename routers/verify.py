from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from models import (
    delete_verification_codes,
    fetch_user_by_email,
    fetch_verification_code,
    get_db,
    verify_user,
    set_user_password,
)
from schemas import (
    BadRequest,
    NotFound,
    TokenResponse,
    VerificationCodeRequest,
)
from utils import (
    create_tokens_for_user,
    verify_verification_token,
)


router = APIRouter(tags=["verify"])

@router.post("/verify-code", response_model=TokenResponse, status_code=status.HTTP_201_CREATED, responses={
    400: {
        "model": BadRequest.error,
        "description": "Bad request (e.g., invalid verification code)"
    },
    404: {
        "model": NotFound.error,
        "description": "User not found"
    }
})
async def verify_user_by_code(request: VerificationCodeRequest, db: Session = Depends(get_db)):
    """Verify user email using verification code"""
    verification_code = fetch_verification_code(db, request.email, request.purpose, request.code)

    if not verification_code:
        raise BadRequest.exception(detail="invalid_code", attr="code")

    user = _cleanup_user_codes(db, request.email, request.purpose)

    if request.purpose == "email_verification":
        user = verify_user(db, user)
    elif request.purpose == "password_reset":
        user = set_user_password(db, user, request.password)

    tokens = create_tokens_for_user(user.email, db)
    return TokenResponse(**tokens)

@router.get("/verify-token", status_code=status.HTTP_200_OK, responses={
    400: {
        "model": BadRequest.error,
        "description": "Bad request (e.g., invalid or expired token)"
    },
    404: {
        "model": NotFound.error,
        "description": "User not found"
    }
})
async def verify_user_by_token(token: str = Query(..., description="Verification token"), db: Session = Depends(get_db)):
    """Verify user email using stateless JWT token"""
    email = verify_verification_token(token)

    user = _cleanup_user_codes(db, email, "email_verification")
    user = verify_user(db, user)

    return Response(content="Success!", status_code=status.HTTP_200_OK, headers={"Content-Type": "text/plain"})

def _cleanup_user_codes(db: Session, email: str, purpose: str):
    user = fetch_user_by_email(db, email)
    if not user:
        raise NotFound.exception(detail="email_not_found", attr="token")
    delete_verification_codes(db, email, purpose)
    return user