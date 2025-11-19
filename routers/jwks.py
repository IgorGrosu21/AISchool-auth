from flask import Blueprint, jsonify

from core import get_jwks as get_jwks_data

router = Blueprint("jwks", __name__)

@router.route("/.well-known/jwks.json", methods=["GET"])
def get_jwks():
    """
    JSON Web Key Set (JWKS) endpoint - RFC 7517
    ---
    tags:
      - jwks
    summary: Get JSON Web Key Set
    description: |
      Returns public keys for JWT verification (RS256).
      This endpoint implements RFC 7517 and supports key rotation - 
      multiple keys can be active simultaneously.
      Only non-expired keys are included in the response.
    produces:
      - application/json
    responses:
      200:
        description: JSON Web Key Set containing public keys for JWT verification
        schema:
          type: object
          properties:
            keys:
              type: array
              items:
                type: object
                properties:
                  kty:
                    type: string
                    example: RSA
                    description: Key type
                  kid:
                    type: string
                    example: abc123
                    description: Key ID (unique identifier)
                  use:
                    type: string
                    example: sig
                    description: Key use (signature)
                  alg:
                    type: string
                    example: RS256
                    description: Algorithm
                  n:
                    type: string
                    description: RSA modulus (base64url encoded)
                  e:
                    type: string
                    description: RSA exponent (base64url encoded)
    """
    return jsonify(get_jwks_data())
