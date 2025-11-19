from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from models import User, get_db
from schemas import Unauthorized

from models import fetch_user_by_email
from .jwt import verify_access_token

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    """Get current authenticated user from JWT token"""
    token = credentials.credentials
    email = verify_access_token(token)["email"]

    user = fetch_user_by_email(db, email)
    if not user:
        raise Unauthorized.exception(detail="user_not_found", attr="email")

    return user
