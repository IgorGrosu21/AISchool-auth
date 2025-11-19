from flask import request
from .validators import validate_email, validate_verification_code, ValidationError
from .errors import BadRequest

def get_verification_code_request():
    """Parse and validate verification code request"""
    from .validators import validate_password
    data = request.get_json() or {}
    try:
        email = validate_email(data.get("email"), required=True)
        code = validate_verification_code(data.get("code"), required=True)
        purpose = data.get("purpose")
        if not purpose:
            raise BadRequest.exception(detail="purpose_required", attr="purpose")
        
        password = None
        if purpose == "password_reset":
            password = validate_password(data.get("password"), required=True)
        
        return {"email": email, "code": code, "password": password, "purpose": purpose}
    except ValidationError as e:
        raise BadRequest.exception(detail=e.message, attr=e.field)

def verification_code_response(purpose: str):
    """Response containing only the verification code"""
    return {"purpose": purpose}
