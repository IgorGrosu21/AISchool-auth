"""Flask schemas for error responses"""
from .errors import ErrorResponse, BadRequestError, UnauthorizedError, ForbiddenError, NotFoundError
from .exceptions import HTTPException, BadRequestException, UnauthorizedException, ForbiddenException, NotFoundException

class BadRequest:
    error = BadRequestError
    exception = BadRequestException

class Unauthorized:
    error = UnauthorizedError
    exception = UnauthorizedException
    
class Forbidden:
    error = ForbiddenError
    exception = ForbiddenException
    
class NotFound:
    error = NotFoundError
    exception = NotFoundException

__all__ = [
    'ErrorResponse', 'HTTPException',
    'BadRequest', 'Unauthorized', 'Forbidden', 'NotFound',
]
