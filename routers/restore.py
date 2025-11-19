from flask import Blueprint, jsonify

from models import (
    fetch_user_by_email,
    get_db,
    create_verification_code,
)
from schemas import (
    BadRequest,
    NotFound,
    get_restore_request,
    verification_code_response,
)
from utils import send_verification_email

router = Blueprint("restore", __name__)

@router.route("/restore", methods=["POST"])
def restore():
    """
    Restore a user password
    ---
    tags:
      - restore
    summary: Request password reset
    description: Request a password reset by sending a verification code to the user's email
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        description: Password restoration data
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
              description: New password (min 8 chars, must contain letters and numbers)
              example: newpassword123
            code:
              type: string
              description: Optional verification code (if already received)
              example: ABC123
    responses:
      200:
        description: Verification code sent successfully
        schema:
          type: object
          properties:
            purpose:
              type: string
              example: password_reset
      400:
        description: Bad request (e.g., password is the same as current password)
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 400
            detail:
              type: string
              example: password_the_same
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
    request_data = get_restore_request()
    db = get_db()

    user = fetch_user_by_email(db, request_data["email"])
    if not user:
        raise NotFound.exception(detail="email_not_found", attr="email")

    if user.check_password(request_data["password"]):
        raise BadRequest.exception(detail="password_the_same", attr="password")

    verification_code = create_verification_code(db, user.email, "password_reset")
    send_verification_email(user.email, verification_code.code, purpose="password_reset")
    return jsonify(verification_code_response("password_reset")), 200
