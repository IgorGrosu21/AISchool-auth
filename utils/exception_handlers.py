from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from schemas import (
    ErrorResponse, HTTPException,
    BadRequest, Unauthorized, Forbidden, NotFound
)

def exception_handler(_request: Request, exc: HTTPException):
    """Handle all exceptions with new error format"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            code=exc.status_code,
            detail=exc.detail,
            attr=exc.attr
        ).model_dump()
    )

async def bad_request_exception_handler(_request: Request, exc: BadRequest.exception):
    """Handle bad request errors with new error format"""
    return exception_handler(_request, exc)

async def unauthorized_exception_handler(_request: Request, exc: Unauthorized.exception):
    """Handle unauthorized errors with new error format"""
    return exception_handler(_request, exc)

async def forbidden_exception_handler(_request: Request, exc: Forbidden.exception):
    """Handle forbidden errors with new error format"""
    return exception_handler(_request, exc)

async def not_found_exception_handler(_request: Request, exc: NotFound.exception):
    """Handle not found errors with new error format"""
    return exception_handler(_request, exc)

async def request_validation_exception_handler(_request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    # Return first validation error (or combine multiple if needed)
    errors = exc.errors()
    if errors:
        first_error = errors[0]
        field_path = '.'.join(str(loc) for loc in first_error.get('loc', []) if loc != 'body')
        return exception_handler(_request, BadRequest.exception(
            detail=first_error.get('type', 'validation_error'),
            attr=field_path if field_path else None
        ))

    # Fallback
    return exception_handler(_request, BadRequest.exception(detail="validation_error"))

exception_handlers = {
  BadRequest.exception: bad_request_exception_handler,
  Unauthorized.exception: unauthorized_exception_handler,
  Forbidden.exception: forbidden_exception_handler,
  NotFound.exception: not_found_exception_handler,
  RequestValidationError: request_validation_exception_handler,
}