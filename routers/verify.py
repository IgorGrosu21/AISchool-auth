from flask import Blueprint, jsonify, request

from models import (
    delete_verification_codes,
    fetch_user_by_email,
    fetch_verification_code,
    get_db,
    verify_user,
    set_user_password,
)
from schemas import (
    BadRequest,
    NotFound,
    token_response,
    get_verification_code_request,
)
from utils import (
    create_tokens_for_user,
    verify_verification_token,
)

router = Blueprint("verify", __name__)

@router.route("/verify-code", methods=["POST"])
def verify_user_by_code():
    """
    Verify user email using verification code
    ---
    tags:
      - verify
    summary: Verify email with code
    description: Verify user email using the verification code sent via email
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        description: Verification code data
        required: true
        schema:
          type: object
          required:
            - email
            - code
            - purpose
          properties:
            email:
              type: string
              format: email
              description: User's email address
              example: user@example.com
            code:
              type: string
              description: 6-character verification code
              example: ABC123
            purpose:
              type: string
              enum: [email_verification, password_reset]
              description: Purpose of verification
              example: email_verification
            password:
              type: string
              description: New password (required for password_reset purpose)
              example: newpassword123
    responses:
      201:
        description: Verification successful
        schema:
          type: object
          properties:
            access:
              type: string
              description: JWT access token (RS256)
              example: eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
            refresh:
              type: string
              description: JWT refresh token (RS256)
              example: eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
      400:
        description: Bad request (e.g., invalid verification code)
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 400
            detail:
              type: string
              example: invalid_code
            attr:
              type: string
              example: code
      404:
        description: User not found
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 404
            detail:
              type: string
              example: email_not_found
            attr:
              type: string
              example: token
    """
    request_data = get_verification_code_request()
    db = get_db()
    
    verification_code = fetch_verification_code(db, request_data["email"], request_data["purpose"], request_data["code"])

    if not verification_code:
        raise BadRequest.exception(detail="invalid_code", attr="code")

    user = _cleanup_user_codes(db, request_data["email"], request_data["purpose"])

    if request_data["purpose"] == "email_verification":
        user = verify_user(db, user)
    elif request_data["purpose"] == "password_reset":
        user = set_user_password(db, user, request_data["password"])

    tokens = create_tokens_for_user(user.email, db)
    return jsonify(token_response(**tokens)), 201

@router.route("/verify-token", methods=["GET"])
def verify_user_by_token():
    """
    Verify user email using stateless JWT token
    ---
    tags:
      - verify
    summary: Verify email with token
    description: Verify user email using the JWT token from the verification link
    produces:
      - text/plain
    parameters:
      - in: query
        name: token
        type: string
        required: true
        description: JWT verification token from email link
        example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    responses:
      200:
        description: Verification successful
        schema:
          type: string
          example: Success!
      400:
        description: Bad request (e.g., invalid or expired token)
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 400
            detail:
              type: string
              example: invalid_or_expired_token
            attr:
              type: string
              example: token
      404:
        description: User not found
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 404
            detail:
              type: string
              example: email_not_found
            attr:
              type: string
              example: token
    """
    token = request.args.get("token")
    if not token:
        raise BadRequest.exception(detail="token_required", attr="token")
    
    db = get_db()
    email = verify_verification_token(token)

    user = _cleanup_user_codes(db, email, "email_verification")
    user = verify_user(db, user)

    return "Success!", 200

def _cleanup_user_codes(db, email: str, purpose: str):
    user = fetch_user_by_email(db, email)
    if not user:
        raise NotFound.exception(detail="email_not_found", attr="token")
    delete_verification_codes(db, email, purpose)
    return user
