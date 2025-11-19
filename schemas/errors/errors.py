from pydantic import BaseModel, Field
from typing import Optional

# Main error response model matching TypeScript IError interface
class ErrorResponse(BaseModel):
    """Standard error response model returned when API requests fail"""
    code: int = Field(..., description="Status code of the error")
    detail: str = Field(..., description="Machine-readable error code (e.g., 'email_already_exists', 'invalid_token', 'user_not_found')")
    attr: Optional[str] = Field(None, description="Optional field name or attribute that the error relates to (e.g., 'email', 'password')")

# Convenience aliases for use in responses parameter
BadRequestError = ErrorResponse
UnauthorizedError = ErrorResponse
ForbiddenError = ErrorResponse
NotFoundError = ErrorResponse