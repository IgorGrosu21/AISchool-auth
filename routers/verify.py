from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from core.database import get_db
from models.models import User
from core.dependencies import get_current_user
from utils.email_utils import generate_verification_token, send_verification_email

router = APIRouter(tags=["verify"])

# Simple token storage for verification (in production, use database or Redis)
verification_tokens = {}  # {email: token}

def verify_token_for_user(user: User, token: str) -> bool:
    """Verify token for user (simplified - in production use proper token generation)"""
    # Check if token matches stored token
    stored_token = verification_tokens.get(user.email)
    if stored_token and stored_token == token:
        return True
    return False

@router.post("/send-verification", status_code=status.HTTP_204_NO_CONTENT)
async def send_verification_email_endpoint(
    current_user: User = Depends(get_current_user),
    _db: Session = Depends(get_db)
):
    """Send verification email to current user"""
    if current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="already_verified"
        )

    # Generate verification token
    token = generate_verification_token(current_user)
    verification_tokens[current_user.email] = token

    # Send email
    send_verification_email(current_user, token)

    return None

@router.get("/verify", status_code=status.HTTP_204_NO_CONTENT)
async def verify_user(
    pk: str = Query(..., description="User email"),
    token: str = Query(..., description="Verification token"),
    db: Session = Depends(get_db)
):
    """Verify user email"""
    try:
        user = db.query(User).filter(User.email == pk).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="user_doesn't_exist"
            )

        # Verify token
        stored_token = verification_tokens.get(user.email)
        if not stored_token or stored_token != token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="incorrect_token"
            )

        # Mark user as verified
        user.is_verified = True
        db.commit()

        # Remove token from storage
        verification_tokens.pop(user.email, None)

        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="incorrect_token"
        ) from e
