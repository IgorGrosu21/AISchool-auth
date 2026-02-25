from shared_backend.services.apps import ServicesConfig as BaseServicesConfig


class ServicesConfig(BaseServicesConfig):
    def ready(self) -> None:
        from services.models import Client

        Client.initialize()

        "No need to fetch jwks on the auth service"
