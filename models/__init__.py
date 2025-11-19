"""Database models"""
from .database import init_db, get_db
from .models import User, RefreshToken, VerificationCode
from .shortcuts import (
  fetch_user_by_email, create_user, verify_user, set_user_password,
  fetch_verification_code, delete_verification_codes, create_verification_code,
  blacklist_refresh_tokens, create_or_update_refresh_token, is_blacklisted,
)

__all__ = [
  'init_db', 'get_db',
  'User', 'RefreshToken', 'VerificationCode',
  'fetch_user_by_email', 'create_user', 'verify_user', 'set_user_password',
  'fetch_verification_code', 'delete_verification_codes', 'create_verification_code',
  'blacklist_refresh_tokens', 'create_or_update_refresh_token', 'is_blacklisted',
]

