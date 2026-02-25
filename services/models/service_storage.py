from typing import cast

from shared_backend.services.models import ServiceStorage as BaseServiceStorage

from .service import Service


class ServiceStorage(BaseServiceStorage):
    _services: dict[str, Service]  # type: ignore

    def serialize_service(self, service_config: dict[str, str]) -> Service:
        return Service(service_config, self._debug)

    def get_service(self, service_id: str) -> Service | None:
        return cast(Service, super().get_service(service_id))
