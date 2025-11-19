from pydantic import BaseModel, field_validator, Field
from typing import Optional
import re

# Restore request schemas
class ValidateExistingEmail(BaseModel):
    """Request schema for validating an existing email"""
    email: str = Field(..., description="User's email address. Will be normalized to lowercase.")

    @field_validator('email')
    @classmethod
    def validate_email(cls, value: str):
        return value.lower().strip()

class ValidateNewEmail(BaseModel):
    """Request schema for validating a new email"""
    email: str = Field(..., description="User's email address. Must be a valid email format. Will be normalized to lowercase.")

    @field_validator('email')
    @classmethod
    def validate_email(cls, value: str):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            raise ValueError('invalid_email_format')

        domain = value.split('@')[1]
        if len(domain) < 3 or '.' not in domain:
            raise ValueError('invalid_email_domain')

        return value.lower().strip()

class ValidateNewPassword(BaseModel):
    """Request schema for validating a password"""
    password: str = Field(..., description="User's password. Must be at least 8 characters long and contain both letters and numbers.")

    @field_validator('password')
    @classmethod
    def validate_password(cls, value: str):
        if len(value) < 8:
            raise ValueError('password_too_small')
        if value.isdigit():
            raise ValueError('password_only_numbers')
        if value.isalpha():
            raise ValueError('password_only_letters')
        return value

class ValidateVerificationCode(BaseModel):
    """Request schema for validating a verification code"""
    code: str = Field(..., description="Verification code. Must be a 6-character alphanumeric code.")

    @field_validator('code')
    @classmethod
    def validate_code(cls, value: str):
        normalized = value.strip().upper()
        if len(normalized) != 6 or not normalized.isalnum():
            raise ValueError('invalid_verification_code')
        return normalized

class ValidateOptionalVerificationCode(ValidateVerificationCode):
    """Request schema for validating an optional verification code"""
    code: Optional[str] = Field(None, description="Verification code. Must be a 6-character alphanumeric code.")

    @field_validator('code')
    @classmethod
    def validate_code(cls, value: Optional[str]):
        if value is None:
            return None
        return super().validate_code(value)