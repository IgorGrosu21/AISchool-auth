from shared_backend.core.settings.auth_schema import (
    JWTServiceAuthSchemeExtension as BaseJWTServiceAuthSchemeExtension,
)
from shared_backend.core.settings.auth_schema import (
    JWTUserAuthSchemeExtension as BaseJWTUserAuthSchemeExtension,
)


class JWTUserAuthSchemeExtension(BaseJWTUserAuthSchemeExtension):  # type: ignore[no-untyped-call]
    target_class = "utils.jwt.authentification.user.JWTUserAuthentication"


class JWTServiceAuthSchemeExtension(BaseJWTServiceAuthSchemeExtension):  # type: ignore[no-untyped-call]
    target_class = "utils.jwt.authentification.service.JWTServiceAuthentication"
