from flask import request
from .errors import BadRequest

def get_refresh_token_request():
    """Parse and validate refresh token request"""
    data = request.get_json() or {}
    refresh = data.get("refresh")
    if not refresh:
        raise BadRequest.exception(detail="refresh_token_required", attr="refresh")
    return {"refresh": refresh}
