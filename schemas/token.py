# Token response schemas - just helper functions for Flask
def access_token_response(access: str):
    """Response containing only the access token"""
    return {"access": access}

def token_response(access: str, refresh: str):
    """Response containing both access and refresh tokens"""
    return {"access": access, "refresh": refresh}
