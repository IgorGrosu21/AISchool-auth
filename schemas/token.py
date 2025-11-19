from pydantic import BaseModel, Field

# Token schemas
class AccessTokenResponse(BaseModel):
    """Response containing only the access token"""
    access: str = Field(..., description="JWT access token (RS256) used for authenticating API requests. Expires after 2 hours.")

class TokenResponse(AccessTokenResponse):
    """Response containing both access and refresh tokens"""
    refresh: str = Field(..., description="JWT refresh token (RS256) used to obtain new access tokens. Expires after 180 days.")