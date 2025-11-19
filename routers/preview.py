from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse

from core import DEBUG
from core.settings import DEFAULT_LANGUAGE
from utils.email import (
    DEFAULT_PURPOSE,
    TEMPLATE_NAMES,
    get_email_template,
)

router = APIRouter(prefix="/preview", tags=["preview"])


@router.get("/emails/{purpose}", response_class=HTMLResponse, include_in_schema=False)
async def preview_email_template(
    purpose: str,
    language: str = Query(DEFAULT_LANGUAGE, description="Language code (en, ro, ru)"),
    username: str = Query("john.doe"),
    code: str = Query("123456"),
    verify_url: Optional[str] = Query(None),
):
    if not DEBUG:
        raise HTTPException(status_code=404, detail="not_found")

    if purpose not in TEMPLATE_NAMES:
        raise HTTPException(status_code=404, detail="unknown_template")

    effective_language, html_template, _ = get_email_template(language, purpose)

    if not verify_url and purpose == DEFAULT_PURPOSE:
        verify_url = "https://example.com/verify?token=dummy"

    html_content = html_template.render(
        username=username,
        code=code,
        verify_url=verify_url,
        language=effective_language,
    )

    return HTMLResponse(content=html_content)


