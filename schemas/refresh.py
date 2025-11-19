from pydantic import BaseModel, Field

# Refresh token schemas
class RefreshTokenRequest(BaseModel):
    """Request schema for token refresh operations"""
    refresh: str = Field(..., description="JWT refresh token (RS256) used to obtain a new access token. Must be a valid, non-expired, and non-blacklisted refresh token.")