from django.contrib.auth.hashers import check_password
from shared_backend.services.models import Service as BaseService


class Service(BaseService):
    _secret_hash: str

    is_authenticated = True  # For JWTServiceAuthentication

    def __init__(self, config: dict[str, str], debug: bool):
        self._secret_hash = config["secret_hash"]
        super().__init__(config, debug)

    def compare_host(self, host: str) -> bool:
        if self._debug:
            return self._dev_url.endswith(host)
        return self._prod_url.endswith(host)

    def compare_secret(self, secret: str) -> bool:
        return check_password(secret, self._secret_hash)
