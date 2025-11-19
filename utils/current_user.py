from flask import request

from models import User, get_db
from schemas import Unauthorized

from models import fetch_user_by_email
from .jwt import verify_access_token

def get_current_user() -> User:
    """Get current authenticated user from JWT token"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise Unauthorized.exception(detail="missing_authorization_header", attr="authorization")
    
    token = auth_header.split(' ')[1]
    email = verify_access_token(token)["email"]

    db = get_db()
    user = fetch_user_by_email(db, email)
    if not user:
        raise Unauthorized.exception(detail="user_not_found", attr="email")

    return user
