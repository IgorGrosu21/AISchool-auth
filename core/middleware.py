"""
Security middleware for Flask REST API
Equivalent to Django's SecurityMiddleware and related security middlewares
"""
from flask import request, redirect
from werkzeug.exceptions import BadRequest

from .localization import normalize_language, set_language
from .settings import (
    ALLOWED_HOSTS,
    CORS_ORIGINS,
    CSP_HEADER,
    DEFAULT_LANGUAGE,
    FORCE_HTTPS,
    HSTS_MAX_AGE,
    SUPPORTED_LANGUAGES,
)

class HTTPSRedirectMiddleware:
    """
    Redirect HTTP requests to HTTPS when FORCE_HTTPS is enabled.
    
    Equivalent to Django's SecurityMiddleware SSL redirect functionality.
    Handles X-Forwarded-Proto header for proxy/load balancer setups.
    """
    def __init__(self):
        self.force_https = FORCE_HTTPS

    def before_request(self):
        # Check if HTTPS redirect is enabled
        if not self.force_https:
            return None

        # Determine if request is secure
        # Check X-Forwarded-Proto header first (common in proxy setups like Render)
        forwarded_proto = request.headers.get("X-Forwarded-Proto", "").lower()
        is_secure = (
            request.scheme == "https" or 
            forwarded_proto == "https"
        )

        # If request is not secure, redirect to HTTPS
        if not is_secure:
            # Build HTTPS URL
            https_url = request.url.replace(scheme="https")
            
            # Return redirect response (308 preserves method)
            return redirect(https_url, code=308)

        return None

    def after_request(self, response):
        return response


class SecurityHeadersMiddleware:
    """
    Add security headers to all responses.
        
    Equivalent to Django's:
    - SecurityMiddleware (HSTS, SSL redirect, security headers)
    - XFrameOptionsMiddleware (X-Frame-Options)
    """
    def __init__(self):
        self.force_https = FORCE_HTTPS
        self.hsts_max_age = HSTS_MAX_AGE

    def before_request(self):
        return None

    def after_request(self, response):
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
        # Check both URL scheme and X-Forwarded-Proto header (for proxy setups)
        forwarded_proto = request.headers.get("X-Forwarded-Proto", "").lower()
        is_secure = (
            request.scheme == "https" or 
            forwarded_proto == "https"
        )
        if self.force_https and is_secure:
            response.headers["Strict-Transport-Security"] = (
                f"max-age={self.hsts_max_age}; includeSubDomains"
            )

        # Content-Security-Policy: More permissive for Swagger UI docs
        path = request.path
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


class TrustedHostMiddleware:
    def __init__(self):
        self.allowed_hosts = ALLOWED_HOSTS

    def before_request(self):
        host = request.host.split(':')[0]  # Remove port if present
        if host not in self.allowed_hosts:
            raise BadRequest("Invalid host header")
        return None

    def after_request(self, response):
        return response


class CorsMiddleware:
    def __init__(self):
        self.allow_origins = CORS_ORIGINS
        self.allow_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
        self.allow_headers = ['*']

    def before_request(self):
        # Handle preflight requests
        if request.method == 'OPTIONS':
            response = self._make_cors_response()
            return response
        return None

    def after_request(self, response):
        # Add CORS headers to all responses
        origin = request.headers.get('Origin')
        if origin in self.allow_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Methods'] = ', '.join(self.allow_methods)
            response.headers['Access-Control-Allow-Headers'] = ', '.join(self.allow_headers)
        return response

    def _make_cors_response(self):
        from flask import make_response
        response = make_response()
        origin = request.headers.get('Origin')
        if origin in self.allow_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Methods'] = ', '.join(self.allow_methods)
            response.headers['Access-Control-Allow-Headers'] = ', '.join(self.allow_headers)
        return response


class LocalizationMiddleware:
    """Middleware to determine preferred language from Accept-Language header."""

    def __init__(self):
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

    def before_request(self):
        language = self._select_language(request.headers.get("accept-language", ""))
        set_language(language)
        request.language = language
        return None

    def after_request(self, response):
        return response
