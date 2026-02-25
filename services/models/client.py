from shared_backend.services.models import Client as BaseClient

from utils.jwt import create_service_token

from .service import Service
from .service_storage import ServiceStorage


class Client(BaseClient):
    _service_storage: ServiceStorage

    @classmethod
    def initialize_storage(cls) -> None:
        cls._service_storage = ServiceStorage(cls._services_config, cls._id, cls._debug)

    @classmethod
    def get_service(cls, service_id: str) -> Service | None:
        return cls._service_storage.get_service(service_id)

    @classmethod
    def auth(cls) -> str:
        token = create_service_token(cls._id)
        cls._token_storage.set_token(token)
        return token
