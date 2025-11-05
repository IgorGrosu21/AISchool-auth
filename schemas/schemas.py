from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
import re

# Token schemas
class TokenResponse(BaseModel):
    access: str
    refresh: str

class AccessTokenResponse(BaseModel):
    access: str

# Auth request schemas
class SignUpRequest(BaseModel):
    email: EmailStr
    password: str

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

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, value: str):
        return value.lower().strip()

# Social login schemas
class SocialLoginRequest(BaseModel):
    token: str
    user_email: Optional[EmailStr] = None

    @field_validator('user_email')
    @classmethod
    def validate_user_email(cls, value: Optional[str]):
        if value:
            return value.lower()
        return value

class GoogleLoginRequest(SocialLoginRequest):
    pass

class FacebookLoginRequest(SocialLoginRequest):
    pass

# Refresh token schemas
class RefreshTokenRequest(BaseModel):
    refresh: str