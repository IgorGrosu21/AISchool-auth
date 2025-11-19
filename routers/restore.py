from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from models import (
    fetch_user_by_email,
    get_db,
    create_verification_code,
)
from schemas import (
    BadRequest,
    NotFound,
    RestoreRequest,
    VerificationCodeResponse,
)
from utils import send_verification_email


router = APIRouter(tags=["restore"])

@router.post("/restore", responses={
    200: {
        "model": VerificationCodeResponse,
        "description": "Further verification required"
    },
    400: {
        "model": BadRequest.error,
        "description": "Bad request"
    },
    404: {
        "model": NotFound.error,
        "description": "User not found"
    }
})
async def restore(request: RestoreRequest, db: Session = Depends(get_db)):
    """Restore a user"""

    user = fetch_user_by_email(db, request.email)
    if not user:
        raise NotFound.exception(detail="email_not_found", attr="email")

    if user.check_password(request.password):
        raise BadRequest.exception(detail="password_the_same", attr="password")

    verification_code = create_verification_code(db, user.email, "password_reset")
    await send_verification_email(user.email, verification_code.code, purpose="password_reset")
    return VerificationCodeResponse(purpose="password_reset")