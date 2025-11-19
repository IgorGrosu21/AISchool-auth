from flask import Blueprint, jsonify

from models import (
    create_user,
    create_verification_code,
    fetch_user_by_email,
    get_db,
    verify_user,
)
from schemas import (
    BadRequest,
    get_login_request,
    get_oauth2_request,
    get_signup_request,
    NotFound,
    token_response,
    verification_code_response,
)
from utils import (
    create_tokens_for_user,
    create_verification_token,
    send_verification_email,
    validate_oauth2_token,
)

router = Blueprint("auth", __name__)

@router.route("/signup", methods=["POST"])
def signup():
    """
    Register a new user
    ---
    tags:
      - auth
    summary: Register a new user
    description: Creates a new user account and sends a verification email
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        description: User registration data
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              format: email
              description: User's email address
              example: user@example.com
            password:
              type: string
              description: User's password (min 8 chars, must contain letters and numbers)
              example: password123
    responses:
      200:
        description: Verification code sent successfully
        schema:
          type: object
          properties:
            purpose:
              type: string
              example: email_verification
      400:
        description: Bad request (e.g., email already exists, invalid email format)
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 400
            detail:
              type: string
              example: email_already_exists
            attr:
              type: string
              example: email
    """
    request_data = get_signup_request()
    db = get_db()

    user = fetch_user_by_email(db, request_data["email"])
    if user:
        raise BadRequest.exception(detail="email_already_exists", attr="email")

    user = create_user(db, request_data["email"], request_data["password"])

    _issue_code_and_tokens(db, user.email)
    return jsonify(verification_code_response("email_verification")), 200

@router.route("/login", methods=["POST"])
def login():
    """
    Login with email and password
    ---
    tags:
      - auth
    summary: User login
    description: Authenticate user with email and password. Returns tokens if verified, otherwise sends verification code.
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        description: Login credentials
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              format: email
              description: User's email address
              example: user@example.com
            password:
              type: string
              description: User's password
              example: password123
    responses:
      200:
        description: Further verification required (user not verified)
        schema:
          type: object
          properties:
            purpose:
              type: string
              example: email_verification
      201:
        description: Login successful
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
        description: Bad request (e.g., incorrect password, password not supported)
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 400
            detail:
              type: string
              example: password_incorrect
            attr:
              type: string
              example: password
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
              example: email
    """
    request_data = get_login_request()
    db = get_db()

    user = fetch_user_by_email(db, request_data["email"])
    if not user:
        raise NotFound.exception(detail="email_not_found", attr="email")

    if not user.has_password() and user.is_verified:
        raise BadRequest.exception(detail="password_not_supported", attr="password")

    if not user.check_password(request_data["password"]):
        raise BadRequest.exception(detail="password_incorrect", attr="password")

    if not user.is_verified:
        _issue_code_and_tokens(db, user.email)
        return jsonify(verification_code_response("email_verification")), 200

    tokens = create_tokens_for_user(user.email, db)
    return jsonify(token_response(**tokens)), 201

@router.route("/oauth2", methods=["POST"])
def oauth2():
    """
    Login with OAuth2 provider token
    ---
    tags:
      - auth
    summary: OAuth2 login
    description: Authenticate user using OAuth2 provider (Google or Facebook) token
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        description: OAuth2 credentials
        required: true
        schema:
          type: object
          required:
            - email
            - token
            - provider
          properties:
            email:
              type: string
              format: email
              description: User's email address
              example: user@example.com
            token:
              type: string
              description: OAuth token obtained from the provider
              example: eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
            provider:
              type: string
              enum: [google, facebook]
              description: OAuth provider name
              example: google
    responses:
      201:
        description: Login successful
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
        description: Bad request (e.g., invalid token, email mismatch, invalid provider)
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 400
            detail:
              type: string
              example: invalid_oauth2_token
            attr:
              type: string
              example: token
    """
    request_data = get_oauth2_request()
    db = get_db()
    
    verified_email = validate_oauth2_token(request_data["provider"], request_data["token"], request_data["email"])

    user = fetch_user_by_email(db, verified_email)
    if not user:
        user = create_user(db, verified_email, is_verified=True)
    else:
        user = verify_user(db, user)

    tokens = create_tokens_for_user(user.email, db)
    return jsonify(token_response(**tokens)), 201

def _issue_code_and_tokens(db, email: str):
    verification_code = create_verification_code(db, email, "email_verification")
    token = create_verification_token(email)

    send_verification_email(email, verification_code.code, token, purpose="email_verification")
