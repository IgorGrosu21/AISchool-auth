import base64
import json
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import TypedDict

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from django.conf import settings
from shared_backend.utils.exceptions import BadRequest

KEYS_DIR: Path = settings.BASE_DIR / "keys"
KEYS_FILE = KEYS_DIR / "rsa_keys.json"


class Keys(TypedDict):
    keys: list[dict[str, str]]
    current_kid: str


class RSAKeyManager:
    """Manages RSA key pairs for JWT signing (singleton via classmethods)"""

    # Class-level state (singleton)
    _keys: Keys | None = None
    _initialized: bool = False

    @classmethod
    def _ensure_initialized(cls) -> Keys:
        """Ensure keys are loaded and initialized"""
        if not cls._initialized:
            cls._initialize()
        assert cls._keys is not None
        return cls._keys

    @classmethod
    def _initialize(cls) -> None:
        """Initialize the key manager (loads keys from file)"""
        cls._ensure_keys_directory()
        cls._load_keys()
        cls._initialized = True

    @classmethod
    def _ensure_keys_directory(cls) -> None:
        """Ensure keys directory exists"""
        KEYS_DIR.mkdir(exist_ok=True)
        (KEYS_DIR / ".gitkeep").touch(exist_ok=True)

    @classmethod
    def _generate_key_pair(cls) -> dict[str, str]:
        """Generate a new RSA key pair"""
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )

        # Get public key
        public_key = private_key.public_key()

        # Serialize keys
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        # Generate key ID
        key_id = cls._generate_key_id()
        now = datetime.now()

        # Key rotation strategy:
        # - signing_expires_at: When key stops being used for signing (1 week)
        # - retires_at: When key can be fully removed (after longest token lifetime: 30 days)
        signing_expires_at = now + timedelta(weeks=1)
        retires_at = now + settings.REFRESH_TOKEN_EXPIRE_LONG  # 30 days - longest token lifetime

        return {
            "kid": key_id,
            "private_key": private_pem.decode("utf-8"),
            "public_key": public_pem.decode("utf-8"),
            "created_at": now.isoformat(),
            "signing_expires_at": signing_expires_at.isoformat(),
            "retires_at": retires_at.isoformat(),
        }

    @classmethod
    def _generate_key_id(cls) -> str:
        """Generate a unique key ID"""
        return secrets.token_urlsafe(16)

    @classmethod
    def _load_keys(cls) -> None:
        """Load keys from file"""
        if not KEYS_FILE.exists():
            # Generate initial key pair
            initial_key = cls._generate_key_pair()
            cls._keys = {"keys": [initial_key], "current_kid": initial_key["kid"]}
            cls._save_keys()
        else:
            with open(KEYS_FILE, encoding="utf-8") as f:
                cls._keys = json.load(f)

            # Clean up retired keys (past retires_at)
            cls._cleanup_retired_keys()

            # Check if current key needs rotation (signing expires within 1 day)
            # Access keys directly to avoid circular call to get_current_key()
            current_kid = cls._keys.get("current_kid")
            if current_kid:
                # Find current key directly from loaded keys
                current_key = next(
                    (k for k in cls._keys.get("keys", []) if k["kid"] == current_kid), None
                )
                if current_key:
                    now = datetime.now()
                    signing_expires_at = datetime.fromisoformat(current_key["signing_expires_at"])
                    if signing_expires_at < now + timedelta(days=1):
                        # Rotate key when signing expires within 1 day
                        cls.rotate_key()

    @classmethod
    def _save_keys(cls) -> None:
        """Save keys to file"""
        with open(KEYS_FILE, "w", encoding="utf-8") as f:
            json.dump(cls._keys, f, indent=2)

    @classmethod
    def _cleanup_retired_keys(cls) -> None:
        """Remove keys that are past their retirement date"""
        now = datetime.now()
        keys_to_remove = []

        keys = cls._keys
        if keys is None:
            keys = cls._ensure_initialized()
        for key in keys.get("keys", []):
            retires_at = datetime.fromisoformat(key["retires_at"])
            if retires_at < now:
                keys_to_remove.append(key["kid"])

        if keys_to_remove:
            keys["keys"] = [k for k in keys["keys"] if k["kid"] not in keys_to_remove]
            # If current key was removed, set a new one
            if keys.get("current_kid") in keys_to_remove:
                if keys["keys"]:
                    # Find the most recent non-expired key for signing
                    valid_keys = []
                    for k in keys["keys"]:
                        signing_expires_at = datetime.fromisoformat(k["signing_expires_at"])
                        if signing_expires_at > now:
                            valid_keys.append(k)

                    if valid_keys:
                        keys["current_kid"] = max(valid_keys, key=lambda x: x["created_at"])["kid"]
                    else:
                        # No valid keys, generate new one
                        new_key = cls._generate_key_pair()
                        keys["keys"].append(new_key)
                        keys["current_kid"] = new_key["kid"]
                else:
                    # No keys left, generate new one
                    new_key = cls._generate_key_pair()
                    keys["keys"] = [new_key]
                    keys["current_kid"] = new_key["kid"]
            cls._keys = keys
            cls._save_keys()

    @classmethod
    def get_current_key(cls) -> dict[str, str] | None:
        """Get the current active private key for signing (not expired for signing)"""
        keys = cls._ensure_initialized()
        current_kid: str | None = keys.get("current_kid")
        if not current_kid:
            return None

        now = datetime.now()
        for key in keys["keys"]:
            if key["kid"] == current_kid:
                # Check if key is still valid for signing
                signing_expires_at = datetime.fromisoformat(key["signing_expires_at"])
                if signing_expires_at > now:
                    return key
        return None

    @classmethod
    def get_private_key(cls, kid: str | None = None) -> bytes | None:
        """Get private key PEM as bytes for signing (only non-expired keys)"""
        keys = cls._ensure_initialized()
        if not kid:
            key_data = cls.get_current_key()
        else:
            # For specific kid, check if it's still valid for signing
            key_data = next((k for k in keys["keys"] if k["kid"] == kid), None)
            if key_data:
                now = datetime.now()
                signing_expires_at = datetime.fromisoformat(key_data["signing_expires_at"])
                if signing_expires_at <= now:
                    # Key expired for signing
                    return None

        if not key_data:
            return None

        return key_data["private_key"].encode("utf-8")

    @classmethod
    def get_public_key(cls, kid: str) -> bytes | None:
        """Get public key PEM as bytes for verification"""
        keys = cls._ensure_initialized()
        # Find key by kid
        key_data = next((k for k in keys["keys"] if k["kid"] == kid), None)

        if not key_data:
            return None

        # Check if key is retired (can't verify with retired keys)
        now = datetime.now()
        retires_at = datetime.fromisoformat(key_data["retires_at"])
        if retires_at <= now:
            return None

        return key_data["public_key"].encode("utf-8")

    @classmethod
    def rotate_key(cls) -> str:
        """Rotate to a new key pair (consistent with refresh token rotation)"""
        # Only ensure initialization if keys aren't already loaded (prevents circular call during _load_keys)
        keys = cls._keys
        if keys is None:
            keys = cls._ensure_initialized()
        # Clean up retired keys first
        cls._cleanup_retired_keys()

        # Generate new key
        new_key = cls._generate_key_pair()
        keys["keys"].append(new_key)
        keys["current_kid"] = new_key["kid"]

        cls._keys = keys
        cls._save_keys()
        return new_key["kid"]

    @classmethod
    def get_jwks(cls) -> list[dict[str, str]]:
        """Get JSON Web Key Set (JWKS) for public keys

        Includes:
        - All keys that are not retired (retires_at > now)
        - This allows verification of tokens signed with expired keys
        - Keys are only removed after retires_at (30 days after creation)
        """
        keys = cls._ensure_initialized()
        jwks: list[dict[str, str]] = []
        now = datetime.now()

        for key_data in keys.get("keys", []):
            # Check if key is retired
            retires_at = datetime.fromisoformat(key_data["retires_at"])
            if retires_at <= now:
                # Key is retired, skip it
                continue

            try:
                # Load public key
                public_key = serialization.load_pem_public_key(
                    key_data["public_key"].encode("utf-8"), backend=default_backend()
                )

                # Get public numbers
                public_numbers = public_key.public_numbers()  # type: ignore

                # Convert to JWK format
                jwk = {
                    "kty": "RSA",
                    "kid": key_data["kid"],
                    "use": "sig",
                    "alg": "RS256",
                    "n": cls._int_to_base64url(public_numbers.n),  # type: ignore
                    "e": cls._int_to_base64url(public_numbers.e),  # type: ignore
                }

                jwks.append(jwk)
            except Exception:
                # Skip invalid keys
                continue

        return jwks

    @classmethod
    def _int_to_base64url(cls, value: int) -> str:
        """Convert integer to base64url encoded string"""
        # Convert integer to bytes
        byte_length = (value.bit_length() + 7) // 8
        bytes_value = value.to_bytes(byte_length, byteorder="big")

        # Encode to base64url
        base64_value = base64.urlsafe_b64encode(bytes_value)
        return base64_value.decode("utf-8").rstrip("=")


def get_private_key(kid: str) -> bytes:
    """Get private key for signing"""
    key = RSAKeyManager.get_private_key(kid)
    if not key:
        raise BadRequest(detail="token_key_not_found", attr="token")
    return key


def get_public_key(kid: str) -> bytes:
    """Get public key for verification"""
    key = RSAKeyManager.get_public_key(kid)
    if not key:
        raise BadRequest(detail="token_key_not_found", attr="token")
    return key


def get_current_kid() -> str:
    """Get current key ID"""
    key = RSAKeyManager.get_current_key()
    if not key:
        raise BadRequest(detail="token_key_not_found", attr="token")
    return key["kid"]


def get_jwks() -> Keys:
    """Get JWKS for public keys"""
    return RSAKeyManager.get_jwks()
