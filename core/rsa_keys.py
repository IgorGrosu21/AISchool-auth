"""
RSA Key Management for JWT RS256 signing
Handles key generation, storage, and rotation
"""
import base64
from datetime import datetime, timedelta, timezone
import json
from typing import Dict, Optional

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from .settings import BASE_DIR

KEYS_DIR = BASE_DIR / "keys"
KEYS_FILE = KEYS_DIR / "rsa_keys.json"


class RSAKeyManager:
    """Manages RSA key pairs for JWT signing"""

    def __init__(self):
        self.keys_dir = KEYS_DIR
        self.keys_file = KEYS_FILE
        self._ensure_keys_directory()
        self._load_keys()

    def _ensure_keys_directory(self):
        """Ensure keys directory exists"""
        self.keys_dir.mkdir(exist_ok=True)
        # Add .gitkeep to ensure directory is tracked
        (self.keys_dir / ".gitkeep").touch(exist_ok=True)

    def _generate_key_pair(self) -> Dict:
        """Generate a new RSA key pair"""
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        # Get public key
        public_key = private_key.public_key()

        # Serialize keys
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        # Generate key ID
        key_id = self._generate_key_id()

        # Calculate expiration (1 week from now)
        expires_at = datetime.now(timezone.utc) + timedelta(weeks=1)

        return {
            "kid": key_id,
            "private_key": private_pem.decode('utf-8'),
            "public_key": public_pem.decode('utf-8'),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": expires_at.isoformat(),
            "active": True
        }

    def _generate_key_id(self) -> str:
        """Generate a unique key ID"""
        import secrets
        return secrets.token_urlsafe(16)

    def _load_keys(self):
        """Load keys from file"""
        if not self.keys_file.exists():
            # Generate initial key pair
            initial_key = self._generate_key_pair()
            self.keys = {
                "keys": [initial_key],
                "current_kid": initial_key["kid"]
            }
            self._save_keys()
        else:
            with open(self.keys_file, 'r', encoding='utf-8') as f:
                self.keys = json.load(f)

            # Check if current key is expired or about to expire (within 1 day)
            current_key = self.get_current_key()
            if current_key:
                expires_at = datetime.fromisoformat(current_key["expires_at"])
                if expires_at < datetime.now(timezone.utc) + timedelta(days=1):
                    # Rotate key when it expires within 1 day
                    self.rotate_key()

    def _save_keys(self):
        """Save keys to file"""
        with open(self.keys_file, 'w', encoding='utf-8') as f:
            json.dump(self.keys, f, indent=2)

    def get_current_key(self) -> Optional[Dict]:
        """Get the current active private key"""
        current_kid = self.keys.get("current_kid")
        if not current_kid:
            return None

        for key in self.keys["keys"]:
            if key["kid"] == current_kid and key.get("active", True):
                return key
        return None

    def get_private_key(self, kid: Optional[str] = None) -> Optional[bytes]:
        """Get private key PEM as bytes"""
        if not kid:
            key_data = self.get_current_key()
        else:
            key_data = next((k for k in self.keys["keys"] if k["kid"] == kid), None)

        if not key_data:
            return None

        return key_data["private_key"].encode('utf-8')

    def rotate_key(self) -> str:
        """Rotate to a new key pair"""
        # Deactivate old keys (keep last 2 active for rotation period)
        active_keys = [k for k in self.keys["keys"] if k.get("active", True)]
        if len(active_keys) > 1:
            # Keep only the most recent key active, mark others as inactive
            sorted_keys = sorted(active_keys, key=lambda x: x["created_at"], reverse=True)
            for key in sorted_keys[1:]:
                key["active"] = False

        # Generate new key
        new_key = self._generate_key_pair()
        self.keys["keys"].append(new_key)
        self.keys["current_kid"] = new_key["kid"]

        self._save_keys()
        return new_key["kid"]

    def get_jwks(self) -> Dict:
        """Get JSON Web Key Set (JWKS) for public keys (only non-expired keys)"""
        jwks = {"keys": []}
        now = datetime.now(timezone.utc)

        # Include only active and non-expired keys
        for key_data in self.keys.get("keys", []):
            if key_data.get("active", True):
                # Check if key is expired
                expires_at = datetime.fromisoformat(key_data["expires_at"])
                if expires_at < now:
                    # Skip expired keys
                    continue

                try:
                    # Load public key
                    public_key = serialization.load_pem_public_key(
                        key_data["public_key"].encode('utf-8'),
                        backend=default_backend()
                    )

                    # Get public numbers
                    public_numbers = public_key.public_numbers()

                    # Convert to JWK format
                    jwk = {
                        "kty": "RSA",
                        "kid": key_data["kid"],
                        "use": "sig",
                        "alg": "RS256",
                        "n": self._int_to_base64url(public_numbers.n),
                        "e": self._int_to_base64url(public_numbers.e)
                    }

                    jwks["keys"].append(jwk)
                except Exception:
                    # Skip invalid keys
                    continue

        return jwks

    def _int_to_base64url(self, value: int) -> str:
        """Convert integer to base64url encoded string"""
        # Convert integer to bytes
        byte_length = (value.bit_length() + 7) // 8
        bytes_value = value.to_bytes(byte_length, byteorder='big')

        # Encode to base64url
        base64_value = base64.urlsafe_b64encode(bytes_value)
        return base64_value.decode('utf-8').rstrip('=')


# Global key manager instance (singleton pattern)
_key_manager: Optional[RSAKeyManager] = None

def get_key_manager() -> RSAKeyManager:
    """Get or create key manager instance"""
    global _key_manager  # pylint: disable=global-statement
    if _key_manager is None:
        _key_manager = RSAKeyManager()
    return _key_manager

def get_private_key(kid: Optional[str] = None) -> bytes:
    """Get private key for signing"""
    manager = get_key_manager()
    return manager.get_private_key(kid)

def get_current_kid() -> str:
    """Get current key ID"""
    manager = get_key_manager()
    key = manager.get_current_key()
    if not key:
        raise ValueError("No active key found")
    return key["kid"]

def get_jwks() -> Dict:
    """Get JWKS for public keys"""
    manager = get_key_manager()
    return manager.get_jwks()

