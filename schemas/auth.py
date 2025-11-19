from pydantic import Field

from .validators import ValidateNewEmail, ValidateExistingEmail, ValidateNewPassword

# Auth request schemas
class SignUpRequest(ValidateNewEmail, ValidateNewPassword):
    """Request schema for user registration"""

class LoginRequest(ValidateExistingEmail):
    """Request schema for email/password login"""
    password: str = Field(..., description="User's password for authentication.")

class OAuth2Request(ValidateExistingEmail):
    """Base request schema for social media OAuth login"""
    token: str = Field(..., description="OAuth token obtained from the social media provider (Google or Facebook).")
    provider: str = Field(..., description="OAuth provider (Google or Facebook).")