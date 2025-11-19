from typing import Optional

class HTTPException(Exception):
    """HTTP exception - always returns a status code"""
    status_code: int
    detail: str
    attr: Optional[str] = None

    def __init__(self, detail: str, attr: Optional[str] = None):
        """
        Args:
            detail: Machine-readable error code (e.g., "email_already_exists", "password_incorrect")
            attr: Optional field name or attribute that the error relates to
        """
        self.detail = detail
        self.attr = attr
        super().__init__(detail)

# HTTPException classes for raising exceptions
class BadRequestException(HTTPException):
    """Bad request exception - always returns 400 status code"""
    status_code: int = 400

class UnauthorizedException(HTTPException):
    """Unauthorized exception - always returns 401 status code"""
    status_code: int = 401

class ForbiddenException(HTTPException):
    """Forbidden exception - always returns 403 status code"""
    status_code: int = 403

class NotFoundException(HTTPException):
    """Not found exception - always returns 404 status code"""
    status_code: int = 404
