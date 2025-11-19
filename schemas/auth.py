from flask import request
from .validators import validate_email, validate_password, ValidationError
from .errors import BadRequest

def get_signup_request():
    """Parse and validate signup request"""
    data = request.get_json() or {}
    try:
        email = validate_email(data.get("email"), required=True)
        password = validate_password(data.get("password"), required=True)
        return {"email": email, "password": password}
    except ValidationError as e:
        raise BadRequest.exception(detail=e.message, attr=e.field)

def get_login_request():
    """Parse and validate login request"""
    data = request.get_json() or {}
    try:
        email = validate_email(data.get("email"), required=True)
        password = data.get("password")
        if not password:
            raise BadRequest.exception(detail="password_required", attr="password")
        return {"email": email, "password": password}
    except ValidationError as e:
        raise BadRequest.exception(detail=e.message, attr=e.field)

def get_oauth2_request():
    """Parse and validate OAuth2 request"""
    data = request.get_json() or {}
    try:
        email = validate_email(data.get("email"), required=True)
        token = data.get("token")
        provider = data.get("provider")
        if not token:
            raise BadRequest.exception(detail="token_required", attr="token")
        if not provider:
            raise BadRequest.exception(detail="provider_required", attr="provider")
        return {"email": email, "token": token, "provider": provider}
    except ValidationError as e:
        raise BadRequest.exception(detail=e.message, attr=e.field)
