from fastapi import APIRouter
from core.rsa_keys import get_jwks as get_jwks_data

router = APIRouter(tags=["jwks"])

@router.get("/jwks.json")
async def get_jwks():
    """
    JSON Web Key Set (JWKS) endpoint
    Returns public keys for JWT verification (RS256)
    Supports key rotation - multiple keys can be active simultaneously
    """
    return get_jwks_data()

