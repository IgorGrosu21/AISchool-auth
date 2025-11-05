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
    ALLOWED_HOSTS = ['localhost', '127.0.0.1'] if DEBUG else []



# RSA Settings

SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required")

ALGORITHM = "RS256"
ACCESS_TOKEN_EXPIRE = timedelta(hours=2)
REFRESH_TOKEN_EXPIRE = timedelta(days=180)



# Email Settings

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True



# Database Settings

DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

