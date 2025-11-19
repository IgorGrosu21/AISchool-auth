"""Shortcuts for database models"""
from .refresh_token import (
    blacklist_refresh_tokens,
    create_or_update_refresh_token,
    is_blacklisted,
)
from .user import fetch_user_by_email, create_user, verify_user, set_user_password
from .verification_code import fetch_verification_code, delete_verification_codes, create_verification_code


__all__ = [
  'blacklist_refresh_tokens', 'create_or_update_refresh_token', 'is_blacklisted',
  'fetch_user_by_email', 'create_user', 'verify_user', 'set_user_password',
  'fetch_verification_code', 'delete_verification_codes', 'create_verification_code',
]