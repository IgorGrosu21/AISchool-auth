from typing import Optional

# Main error response model matching TypeScript IError interface
class ErrorResponse:
    """Standard error response model returned when API requests fail"""
    def __init__(self, code: int, detail: str, attr: Optional[str] = None):
        self.code = code
        self.detail = detail
        self.attr = attr
    
    def to_dict(self):
        return {
            "code": self.code,
            "detail": self.detail,
            "attr": self.attr
        }

# Convenience aliases for use in responses parameter
BadRequestError = ErrorResponse
UnauthorizedError = ErrorResponse
ForbiddenError = ErrorResponse
NotFoundError = ErrorResponse
