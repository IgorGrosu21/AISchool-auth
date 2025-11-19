from pydantic import BaseModel, Field

from .validators import ValidateExistingEmail, ValidateVerificationCode

# Verification schemas
class VerificationCodeRequest(ValidateExistingEmail, ValidateVerificationCode):
    """Request schema for verifying a verification code"""
    password: str = Field(..., description="User's password for authentication.")
    purpose: str = Field(..., description="Purpose of the verification code.")

class VerificationCodeResponse(BaseModel):
    """Response containing only the verification code"""
    purpose: str = Field(..., description="Purpose of the verification code.")