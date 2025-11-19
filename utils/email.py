from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from aiosmtplib import SMTP
from jinja2 import Environment, FileSystemLoader, TemplateNotFound, select_autoescape

from core import (
    BASE_DIR,
    EMAIL_HOST,
    EMAIL_HOST_PASSWORD,
    EMAIL_HOST_USER,
    EMAIL_PORT,
    HOST,
)
from core import get_language
from core.settings import DEFAULT_LANGUAGE

DEFAULT_PURPOSE = "email_verification"

TEMPLATE_ENV = Environment(
    loader=FileSystemLoader(BASE_DIR / "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)

TEMPLATE_NAMES = {
    "email_verification": "verify_email",
    "password_reset": "restore_password",
}

EMAIL_SUBJECTS = {
    "email_verification": {
        "en": "Confirm your account",
        "ro": "Confirmă-ți contul",
        "ru": "Подтвердите свой аккаунт",
    },
    "password_reset": {
        "en": "Reset your password",
        "ro": "Resetează-ți parola",
        "ru": "Сбросьте свой пароль",
    },
}


def _resolve_template_paths(language: str = DEFAULT_LANGUAGE, purpose: str = DEFAULT_PURPOSE):
    templates_dir = BASE_DIR / "templates" / "emails"
    template_key = TEMPLATE_NAMES.get(purpose, TEMPLATE_NAMES[DEFAULT_PURPOSE])
    html_template_name = f"emails/{language}/{template_key}.html"
    text_template_path = templates_dir / language / f"{template_key}.txt"

    try:
        TEMPLATE_ENV.get_template(html_template_name)
    except TemplateNotFound:
        language = DEFAULT_LANGUAGE
        html_template_name = f"emails/{language}/{template_key}.html"
        text_template_path = templates_dir / language / f"{template_key}.txt"

    if not text_template_path.exists():
        language = DEFAULT_LANGUAGE
        text_template_path = templates_dir / language / f"{template_key}.txt"
        html_template_name = f"emails/{language}/{template_key}.html"

    return language, html_template_name, text_template_path


def _get_email_subject(language: str, purpose: str) -> str:
    purpose_subjects = EMAIL_SUBJECTS.get(purpose, {})
    return (
        purpose_subjects.get(language)
        or purpose_subjects.get(DEFAULT_LANGUAGE)
        or "AISchool notification"
    )


def get_email_template(language: str, purpose: str):
    """Resolve and load the HTML email template for preview purposes."""
    language, html_template_name, text_template_path = _resolve_template_paths(language, purpose)
    html_template = TEMPLATE_ENV.get_template(html_template_name)
    return language, html_template, text_template_path


async def send_verification_email(
    email: str,
    code: Optional[str] = None,
    token: Optional[str] = None,
    purpose: str = DEFAULT_PURPOSE,
):
    """Send verification email to user"""
    verify_link: Optional[str] = None
    if token:
        verify_link = f"{HOST}/verify-token?token={token}"

    language = get_language()
    language, html_template_name, text_template_path = _resolve_template_paths(language, purpose)
    html_template = TEMPLATE_ENV.get_template(html_template_name)

    html_content = html_template.render(
        username=email.split("@")[0],
        verify_url=verify_link,
        code=code,
        language=language,
    )

    with open(text_template_path, "r", encoding="utf-8") as f:
        text_template_content = f.read()
    text_content = text_template_content.format(
        username=email.split("@")[0],
        verify_url=verify_link or "",
        code=code,
        language=language,
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = _get_email_subject(language, purpose)
    msg["From"] = EMAIL_HOST_USER
    msg["To"] = email

    part1 = MIMEText(text_content, "plain", "utf-8")
    part2 = MIMEText(html_content, "html", "utf-8")

    msg.attach(part1)
    msg.attach(part2)

    server = SMTP(
        hostname=EMAIL_HOST,
        port=EMAIL_PORT,
        username=EMAIL_HOST_USER,
        password=EMAIL_HOST_PASSWORD,
        use_tls=True
    )
    async with server:
        await server.send_message(msg)
