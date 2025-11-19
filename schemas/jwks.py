# JWKS schemas - just return dict directly in Flask
def jwks_response(keys: list):
    """JSON Web Key Set (JWKS) response - RFC 7517 standard format"""
    return {"keys": keys}
