from datetime import timedelta
import os
from pathlib import Path

import dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

dotenv.load_dotenv(BASE_DIR / '.env')

# General Settings

DEBUG = bool(int(os.environ.get('DEBUG', '0')))
if not DEBUG and os.environ.get('ENVIRONMENT') == 'production':
    DEBUG = False

HOST = os.environ.get('HOST')
if not HOST:
    raise ValueError("HOST environment variable is required")

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
if not ALLOWED_HOSTS or ALLOWED_HOSTS == ['']:
    raise ValueError("ALLOWED_HOSTS environment variable is required")

CORS_ORIGINS = os.environ.get('CORS_ORIGINS').split(',')
if not CORS_ORIGINS or CORS_ORIGINS == ['']:
    raise ValueError("CORS_ORIGINS environment variable is required")

FORCE_HTTPS = bool(int(os.environ.get('FORCE_HTTPS', '0')))
HSTS_MAX_AGE = int(os.environ.get('HSTS_MAX_AGE', '31536000'))
CSP_HEADER= os.environ.get('CSP_HEADER')
if not CSP_HEADER:
    raise ValueError("CSP_HEADER environment variable is required")



# RSA Settings

SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required")

ALGORITHM = "RS256"
ACCESS_TOKEN_EXPIRE = timedelta(hours=2)
REFRESH_TOKEN_EXPIRE = timedelta(days=180)



# Email Settings

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
VERIFICATION_TIMEOUT = timedelta(minutes=1)
VERIFICATION_TOKEN_EXPIRE = timedelta(minutes=30)
VERIFICATION_SECRET = os.environ.get('VERIFICATION_SECRET')
if not VERIFICATION_SECRET:
    raise ValueError("VERIFICATION_SECRET environment variable is required")



# Localization Settings

SUPPORTED_LANGUAGES = ('en', 'ru', 'ro')
DEFAULT_LANGUAGE = 'en'



# Database Settings

DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")



# OAuth2 Settings

GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
if not GOOGLE_CLIENT_ID:
    raise ValueError("GOOGLE_CLIENT_ID environment variable is required")

FACEBOOK_CLIENT_ID = os.environ.get('FACEBOOK_CLIENT_ID')
if not FACEBOOK_CLIENT_ID:
    raise ValueError("FACEBOOK_CLIENT_ID environment variable is required")