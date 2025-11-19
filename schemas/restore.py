from flask import request
from .validators import validate_email, validate_password, validate_verification_code, ValidationError
from .errors import BadRequest

def get_restore_request():
    """Parse and validate restore request"""
    data = request.get_json() or {}
    try:
        email = validate_email(data.get("email"), required=True)
        password = validate_password(data.get("password"), required=True)
        code = validate_verification_code(data.get("code"), required=False)
        return {"email": email, "password": password, "code": code}
    except ValidationError as e:
        raise BadRequest.exception(detail=e.message, attr=e.field)
