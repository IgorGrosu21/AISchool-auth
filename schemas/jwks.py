from pydantic import BaseModel, Field
from typing import List

# JWKS schemas (RFC 7517)
class JWK(BaseModel):
    """JSON Web Key (JWK) - represents a single public key in JWKS format (RFC 7517)"""
    kty: str = Field(..., description="Key type. Always 'RSA' for RSA public keys.")
    kid: str = Field(..., description="Key ID (kid) - unique identifier for this key. Used in JWT header to specify which key to use for verification.")
    use: str = Field(..., description="Key use. Always 'sig' (signature) for JWT signing/verification keys.")
    alg: str = Field(..., description="Algorithm. Always 'RS256' (RSA with SHA-256) for this implementation.")
    n: str = Field(..., description="RSA modulus (n) - the public modulus of the RSA key pair, base64url encoded without padding.")
    e: str = Field(..., description="RSA exponent (e) - the public exponent of the RSA key pair, base64url encoded without padding. Typically 'AQAB' (65537).")

class JWKSResponse(BaseModel):
    """JSON Web Key Set (JWKS) response - RFC 7517 standard format for publishing public keys"""
    keys: List[JWK] = Field(..., description="Array of JSON Web Keys. Contains all active, non-expired public keys available for JWT verification. Supports key rotation with multiple active keys.")