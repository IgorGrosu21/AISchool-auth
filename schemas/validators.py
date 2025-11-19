import re
from typing import Optional

class ValidationError(Exception):
    """Base validation error"""
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(message)

def validate_email(value: str, required: bool = True) -> str:
    """Validate and normalize email"""
    if not value and not required:
        return value
    if not value:
        raise ValidationError("email_required", "email")
    
    value = value.lower().strip()
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, value):
        raise ValidationError("invalid_email_format", "email")
    
    domain = value.split('@')[1]
    if len(domain) < 3 or '.' not in domain:
        raise ValidationError("invalid_email_domain", "email")
    
    return value

def validate_password(value: str, required: bool = True) -> str:
    """Validate password"""
    if not value and not required:
        return value
    if not value:
        raise ValidationError("password_required", "password")
    
    if len(value) < 8:
        raise ValidationError("password_too_small", "password")
    if value.isdigit():
        raise ValidationError("password_only_numbers", "password")
    if value.isalpha():
        raise ValidationError("password_only_letters", "password")
    
    return value

def validate_verification_code(value: Optional[str], required: bool = True) -> Optional[str]:
    """Validate verification code"""
    if value is None:
        if required:
            raise ValidationError("code_required", "code")
        return None
    
    normalized = value.strip().upper()
    if len(normalized) != 6 or not normalized.isalnum():
        raise ValidationError("invalid_verification_code", "code")
    
    return normalized
