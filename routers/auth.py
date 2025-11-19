from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from models import (
    create_user,
    create_verification_code,
    fetch_user_by_email,
    get_db,
    verify_user,
)
from schemas import (
    BadRequest,
    LoginRequest,
    NotFound,
    OAuth2Request,
    SignUpRequest,
    TokenResponse,
    VerificationCodeResponse,
)
from utils import (
    create_tokens_for_user,
    create_verification_token,
    send_verification_email,
    validate_oauth2_token,
)


router = APIRouter(tags=["auth"])

@router.post("/signup", status_code=status.HTTP_200_OK, response_model=VerificationCodeResponse, responses={
    400: {
        "model": BadRequest.error,
        "description": "Bad request"
    }
})
async def signup(request: SignUpRequest, db: Session = Depends(get_db)):
    """Register a new user"""

    user = fetch_user_by_email(db, request.email)
    if user:
        raise BadRequest.exception(detail="email_already_exists", attr="email")

    user = create_user(db, request.email, request.password)

    await _issue_code_and_tokens(db, user.email)
    return VerificationCodeResponse(purpose="email_verification")

@router.post("/login", status_code=status.HTTP_201_CREATED, response_model=TokenResponse, responses={
    200: {
        "model": VerificationCodeResponse,
        "description": "Further verification required"
    },
    400: {
        "model": BadRequest.error,
        "description": "Bad request (e.g., incorrect password)"
    },
    404: {
        "model": NotFound.error,
        "description": "User not found"
    }
})
async def login(request: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """Login with email and password"""

    user = fetch_user_by_email(db, request.email)
    if not user:
        raise NotFound.exception(detail="email_not_found", attr="email")

    if not user.has_password() and user.is_verified:
        raise BadRequest.exception(detail="password_not_supported", attr="password")

    if not user.check_password(request.password):
        raise BadRequest.exception(detail="password_incorrect", attr="password")

    if not user.is_verified:
        response.status_code = status.HTTP_200_OK

        await _issue_code_and_tokens(db, user.email)
        return VerificationCodeResponse(purpose="email_verification")

    tokens = create_tokens_for_user(user.email, db)
    return TokenResponse(**tokens)

@router.post("/oauth2", status_code=status.HTTP_201_CREATED, response_model=TokenResponse, responses={
    400: {
        "model": BadRequest.error,
        "description": "Bad request (e.g., invalid token, email mismatch)"
    }
})
async def oauth2(request: OAuth2Request, db: Session = Depends(get_db)):
    """Login with OAuth2 provider token"""
    verified_email = await validate_oauth2_token(request.provider, request.token, request.email)

    user = fetch_user_by_email(db, verified_email)
    if not user:
        user = create_user(db, verified_email, is_verified=True)
    else:
        user = verify_user(db, user)

    tokens = create_tokens_for_user(user.email, db)
    return TokenResponse(**tokens)

async def _issue_code_and_tokens(db: Session, email: str):
    verification_code = create_verification_code(db, email, "email_verification")
    token = create_verification_token(email)

    await send_verification_email(email, verification_code.code, token, purpose="email_verification")