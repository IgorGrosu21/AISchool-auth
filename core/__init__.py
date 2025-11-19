"""Core application files"""
from .settings import (
    BASE_DIR, DEBUG, HOST,
    ALLOWED_HOSTS, CORS_ORIGINS, FORCE_HTTPS, HSTS_MAX_AGE, CSP_HEADER,
    ALGORITHM, ACCESS_TOKEN_EXPIRE, REFRESH_TOKEN_EXPIRE,
    EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, VERIFICATION_TIMEOUT, VERIFICATION_TOKEN_EXPIRE, VERIFICATION_SECRET,
    DATABASE_URL,
    GOOGLE_CLIENT_ID, FACEBOOK_CLIENT_ID,
)
from .rsa_keys import get_key_manager, get_current_kid, get_jwks, get_private_key
from .localization import get_language
from .middleware import (
    SecurityHeadersMiddleware,
    TrustedHostMiddleware,
    CorsMiddleware,
    LocalizationMiddleware,
    TrailingSlashMiddleware
)

# Build middleware stack conditionally
MIDDLEWARE_STACK = [
    TrailingSlashMiddleware,
    LocalizationMiddleware,
    SecurityHeadersMiddleware,
    TrustedHostMiddleware,
    CorsMiddleware,
]

# Only add HTTPS redirect in production when FORCE_HTTPS is enabled
if FORCE_HTTPS:
    from .middleware import HTTPSRedirectMiddleware
    # Add at the beginning (will execute last) to redirect HTTP to HTTPS
    MIDDLEWARE_STACK.insert(0, HTTPSRedirectMiddleware)

__all__ = [
    'BASE_DIR', 'DEBUG', 'HOST',
    'ALLOWED_HOSTS', 'CORS_ORIGINS', 'FORCE_HTTPS', 'HSTS_MAX_AGE', 'CSP_HEADER',
    'ALGORITHM', 'ACCESS_TOKEN_EXPIRE', 'REFRESH_TOKEN_EXPIRE',
    'EMAIL_HOST', 'EMAIL_PORT', 'EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD', 'VERIFICATION_TIMEOUT', 'VERIFICATION_TOKEN_EXPIRE', 'VERIFICATION_SECRET',
    'DATABASE_URL',
    'GOOGLE_CLIENT_ID', 'FACEBOOK_CLIENT_ID',
    'get_language',
    'get_key_manager', 'get_current_kid', 'get_jwks', 'get_private_key',
    'MIDDLEWARE_STACK',
]
