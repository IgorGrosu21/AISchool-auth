from flask import Blueprint, request

from core import DEBUG
from core.settings import DEFAULT_LANGUAGE
from utils.email import (
    DEFAULT_PURPOSE,
    TEMPLATE_NAMES,
    get_email_template,
)

router = Blueprint("preview", __name__, url_prefix="/preview")

@router.route("/emails/<purpose>", methods=["GET"])
def preview_email_template(purpose: str):
    """
    Preview email template (debug only)
    ---
    tags:
      - preview
    summary: Preview email template
    description: |
      Preview email templates in HTML format. Only available when DEBUG=True.
      This endpoint is useful for testing email templates during development.
    produces:
      - text/html
    parameters:
      - in: path
        name: purpose
        type: string
        required: true
        enum: [email_verification, password_reset]
        description: Purpose of the email template
        example: email_verification
      - in: query
        name: language
        type: string
        required: false
        enum: [en, ru, ro]
        default: en
        description: Language code
        example: en
      - in: query
        name: username
        type: string
        required: false
        default: john.doe
        description: Username to display in template
        example: john.doe
      - in: query
        name: code
        type: string
        required: false
        default: 123456
        description: Verification code to display
        example: ABC123
      - in: query
        name: verify_url
        type: string
        required: false
        description: Verification URL to display
        example: https://example.com/verify?token=dummy
    responses:
      200:
        description: HTML email template preview
        schema:
          type: string
      404:
        description: Not found (when DEBUG=False or unknown template)
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 404
            detail:
              type: string
              example: not_found
    """
    if not DEBUG:
        from schemas import NotFound
        raise NotFound.exception(detail="not_found")
    
    if purpose not in TEMPLATE_NAMES:
        from schemas import NotFound
        raise NotFound.exception(detail="unknown_template")

    language = request.args.get("language", DEFAULT_LANGUAGE)
    username = request.args.get("username", "john.doe")
    code = request.args.get("code", "123456")
    verify_url = request.args.get("verify_url")

    effective_language, html_template, _ = get_email_template(language, purpose)

    if not verify_url and purpose == DEFAULT_PURPOSE:
        verify_url = "https://example.com/verify?token=dummy"

    html_content = html_template.render(
        username=username,
        code=code,
        verify_url=verify_url,
        language=effective_language,
    )

    return html_content, 200, {"Content-Type": "text/html"}
