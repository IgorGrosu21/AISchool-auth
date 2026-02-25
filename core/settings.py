from datetime import timedelta
from pathlib import Path

from shared_backend.core.settings.helpers import get_env, load_environment, setup_base_dir

BASE_DIR = setup_base_dir(Path(__file__))
load_environment(BASE_DIR)


from shared_backend.core.settings.defaults import *
from shared_backend.core.settings.defaults import (
    REST_FRAMEWORK,
    setup_databases,
    setup_static_files,
)

REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "utils.jwt.authentification.user.JWTUserAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
}

from .auth_schema import *

DATABASES = setup_databases(BASE_DIR)

static_files_dict = setup_static_files(BASE_DIR)

STATIC_URL = static_files_dict["STATIC_URL"]
STATIC_ROOT = static_files_dict["STATIC_ROOT"]

MEDIA_URL = static_files_dict["MEDIA_URL"]
MEDIA_ROOT = static_files_dict["MEDIA_ROOT"]

PUBLIC_URL = static_files_dict["PUBLIC_URL"]
PUBLIC_ROOT = static_files_dict["PUBLIC_ROOT"]

# JWT Settings
ALGORITHM = "RS256"
ACCESS_TOKEN_EXPIRE = timedelta(minutes=30)  # 30 minutes
REFRESH_TOKEN_EXPIRE_SHORT = timedelta(days=1)  # 1 day (default, no remember_me)
REFRESH_TOKEN_EXPIRE_LONG = timedelta(days=30)  # 30 days (remember_me=True)
SERVICE_TOKEN_EXPIRE = timedelta(hours=2)  # 2 hours

VERIFICATION_TIMEOUT = timedelta(minutes=1)
VERIFICATION_TOKEN_EXPIRE = timedelta(minutes=30)

# OAuth2 Settings
GOOGLE_CLIENT_ID = get_env("GOOGLE_CLIENT_ID")
FACEBOOK_CLIENT_ID = get_env("FACEBOOK_CLIENT_ID")
