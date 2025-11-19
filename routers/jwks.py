from fastapi import APIRouter

from core import get_jwks as get_jwks_data
from schemas import JWKSResponse

router = APIRouter(tags=["jwks"])

@router.get(
    "/.well-known/jwks.json",
    response_model=JWKSResponse,
    summary="JSON Web Key Set (JWKS)",
    description=(
        "Returns public keys for JWT verification (RS256). "
        "This endpoint implements RFC 7517 and supports key rotation - "
        "multiple keys can be active simultaneously. "
        "Only non-expired keys are included in the response."
    ),
    responses={
        200: {
            "model": JWKSResponse,
            "description": "JSON Web Key Set containing public keys for JWT verification"
        }
    }
)
async def get_jwks():
    """
    JSON Web Key Set (JWKS) endpoint - RFC 7517
    
    Returns public keys for JWT verification (RS256).
    Supports key rotation - multiple keys can be active simultaneously.
    Only non-expired keys are returned.
    """
    return get_jwks_data()

