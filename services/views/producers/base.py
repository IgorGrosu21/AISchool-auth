from typing import TypeVar

from django.db.models import Model
from rest_framework.serializers import Serializer
from shared_backend.services.views import BaseProducerView as BaseBaseProducerView

from utils.jwt.authentification.service import JWTServiceAuthentication

_IN = TypeVar("_IN", bound=Serializer[Model])


class BaseProducerView(BaseBaseProducerView[_IN]):
    authentication_classes = [JWTServiceAuthentication]
    allowed_services = "*"
