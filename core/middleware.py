"""
Security middleware for FastAPI REST API
Equivalent to Django's SecurityMiddleware and related security middlewares
"""
from fastapi.middleware.cors import CORSMiddleware as BaseCorsMiddleware
from fastapi.middleware.trustedhost import (
  TrustedHostMiddleware as BaseTrustedHostMiddleware,
)
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.types import ASGIApp

from .localization import normalize_language, reset_language, set_language
from .settings import (
  ALLOWED_HOSTS,
  CORS_ORIGINS,
  CSP_HEADER,
  DEFAULT_LANGUAGE,
  FORCE_HTTPS,
  HSTS_MAX_AGE,
  SUPPORTED_LANGUAGES,
)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
  """
  Add security headers to all responses.
      
  Equivalent to Django's:
  - SecurityMiddleware (HSTS, SSL redirect, security headers)
  - XFrameOptionsMiddleware (X-Frame-Options)
  """

  def __init__(self, app: ASGIApp):
    super().__init__(app)

    # Security headers configuration
    self.force_https = FORCE_HTTPS
    self.hsts_max_age = HSTS_MAX_AGE

  async def dispatch(self, request: Request, call_next):
    response = await call_next(request)

    # X-Frame-Options: Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"

    # X-Content-Type-Options: Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"

    # X-XSS-Protection: Enable XSS filtering
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # Referrer-Policy: Control referrer information
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Permissions-Policy: Control browser features
    response.headers["Permissions-Policy"] = (
      "geolocation=(), microphone=(), camera=()"
    )

    # Strict-Transport-Security (HSTS): Force HTTPS
    if self.force_https and request.url.scheme == "https":
      response.headers["Strict-Transport-Security"] = (
        f"max-age={self.hsts_max_age}; includeSubDomains"
      )

    # Content-Security-Policy: More permissive for Swagger UI docs
    path = request.url.path
    if path.startswith("/docs") or path.startswith("/redoc") or path.startswith("/openapi.json") or path.startswith("/preview"):
      # Permissive CSP for Swagger UI - allows CDN resources and inline scripts
      response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data: https://fastapi.tiangolo.com https://cdn.jsdelivr.net https://cdn-icons-png.flaticon.com https://aischool.md; "
        "font-src 'self' https://cdn.jsdelivr.net; "
        "connect-src 'self' https://cdn.jsdelivr.net"
      )
    else:
      # Restrictive CSP for API endpoints
      response.headers["Content-Security-Policy"] = CSP_HEADER

    return response


class TrustedHostMiddleware(BaseTrustedHostMiddleware):
  def __init__(self, app: ASGIApp):
    super().__init__(
      app,
      allowed_hosts=ALLOWED_HOSTS,
      www_redirect=False
    )

class CorsMiddleware(BaseCorsMiddleware):
  def __init__(self, app: ASGIApp):
    super().__init__(
      app,
      allow_origins=CORS_ORIGINS,
      allow_credentials=True,
      allow_methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
      allow_headers=['*'],
    )


class LocalizationMiddleware(BaseHTTPMiddleware):
  """Middleware to determine preferred language from Accept-Language header."""

  def __init__(self, app: ASGIApp):
    super().__init__(app)
    self.supported = set(SUPPORTED_LANGUAGES)

  def _select_language(self, header_value: str) -> str:
    if not header_value:
      return DEFAULT_LANGUAGE

    for item in header_value.split(","):
      lang = item.split(";")[0].strip().lower()
      if not lang:
        continue

      normalized = normalize_language(lang, self.supported)
      if normalized in self.supported:
        return normalized

    return DEFAULT_LANGUAGE

  async def dispatch(self, request: Request, call_next):
    language = self._select_language(request.headers.get("accept-language", ""))
    token = set_language(language)
    request.state.language = language

    try:
      response = await call_next(request)
    finally:
      reset_language(token)

    return response