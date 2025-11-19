from flask import Blueprint, jsonify
from jose import jwt

from models import (
    blacklist_refresh_tokens,
    create_or_update_refresh_token,
    get_db,
    is_blacklisted,
)
from schemas import (
    access_token_response,
    BadRequest,
    get_refresh_token_request,
    Unauthorized,
)
from utils import create_access_token, get_current_user, verify_refresh_token

router = Blueprint("refresh", __name__)

@router.route("/refresh", methods=["POST"])
def refresh_token():
    """
    Refresh access token using refresh token
    ---
    tags:
      - refresh
    summary: Refresh access token
    description: Get a new access token using a valid refresh token
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        description: Refresh token data
        required: true
        schema:
          type: object
          required:
            - refresh
          properties:
            refresh:
              type: string
              description: JWT refresh token (RS256)
              example: eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
    responses:
      200:
        description: New access token generated
        schema:
          type: object
          properties:
            access:
              type: string
              description: JWT access token (RS256)
              example: eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
      400:
        description: Bad request (e.g., missing or invalid refresh token)
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 400
            detail:
              type: string
              example: invalid_refresh_token
            attr:
              type: string
              example: refresh
      401:
        description: Unauthorized (e.g., token blacklisted)
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 401
            detail:
              type: string
              example: invalid_refresh_token
            attr:
              type: string
              example: refresh
    """
    request_data = get_refresh_token_request()
    db = get_db()
    
    if not request_data["refresh"]:
        raise BadRequest.exception(detail="no_refresh_token", attr="refresh")

    try:
        token_data = verify_refresh_token(request_data["refresh"])
        email, jti = token_data.get("email"), token_data.get("jti")

        if is_blacklisted(db, jti):
            raise Unauthorized.exception(detail="invalid_refresh_token", attr="refresh")

        access_token = create_access_token({"email": email})

        return jsonify(access_token_response(access_token)), 200
    except (BadRequest.exception, Unauthorized.exception):
        raise
    except Exception as e:
        raise BadRequest.exception(detail="invalid_refresh_token", attr="refresh") from e

@router.route("/logout", methods=["POST"])
def logout():
    """
    Logout by blacklisting refresh token
    ---
    tags:
      - refresh
    summary: Logout
    description: Logout by blacklisting the provided refresh token
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        description: Refresh token to blacklist
        required: false
        schema:
          type: object
          properties:
            refresh:
              type: string
              description: JWT refresh token to blacklist
              example: eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
    responses:
      204:
        description: Logout successful (no content)
    """
    request_data = get_refresh_token_request()
    db = get_db()
    
    if not request_data.get("refresh"):
        return "", 204

    try:
        unverified = jwt.get_unverified_header(request_data["refresh"])
        kid = unverified.get("kid")

        if kid:
            payload = verify_refresh_token(request_data["refresh"])
            email, jti, exp = payload.get("email"), payload.get("jti"), payload.get("exp")
            if email and jti:
                create_or_update_refresh_token(db, {
                    "user_email": email,
                    "expires_at": exp,
                    "jti": jti,
                    "is_blacklisted": True,
                })
    except Exception:
        pass

    return "", 204

@router.route("/logout-all", methods=["POST"])
def logout_all():
    """
    Logout from all devices (blacklist all user tokens)
    ---
    tags:
      - refresh
    summary: Logout from all devices
    description: Blacklist all refresh tokens for the current authenticated user
    consumes:
      - application/json
    produces:
      - application/json
    security:
      - Bearer: []
    responses:
      204:
        description: Logout from all devices successful (no content)
      401:
        description: Unauthorized (missing or invalid token)
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 401
            detail:
              type: string
              example: missing_authorization_header
            attr:
              type: string
              example: authorization
    """
    current_user = get_current_user()
    db = get_db()
    blacklist_refresh_tokens(db, current_user.email)
    return "", 204
