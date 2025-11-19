from flask import jsonify
from werkzeug.exceptions import BadRequest as WerkzeugBadRequest

from schemas import (
    ErrorResponse, HTTPException,
    BadRequest, Unauthorized, Forbidden, NotFound
)

def exception_handler(exc: HTTPException):
    """Handle all exceptions with new error format"""
    return jsonify(ErrorResponse(
        code=exc.status_code,
        detail=exc.detail,
        attr=exc.attr
    ).to_dict()), exc.status_code

def bad_request_exception_handler(exc: BadRequest.exception):
    """Handle bad request errors with new error format"""
    return exception_handler(exc)

def unauthorized_exception_handler(exc: Unauthorized.exception):
    """Handle unauthorized errors with new error format"""
    return exception_handler(exc)

def forbidden_exception_handler(exc: Forbidden.exception):
    """Handle forbidden errors with new error format"""
    return exception_handler(exc)

def not_found_exception_handler(exc: NotFound.exception):
    """Handle not found errors with new error format"""
    return exception_handler(exc)

def request_validation_exception_handler(exc):
    """Handle request validation errors"""
    # Try to extract field information from the exception
    if hasattr(exc, 'description'):
        detail = exc.description
    else:
        detail = "validation_error"
    
    return exception_handler(BadRequest.exception(detail=detail))

exception_handlers = {
    BadRequest.exception: bad_request_exception_handler,
    Unauthorized.exception: unauthorized_exception_handler,
    Forbidden.exception: forbidden_exception_handler,
    NotFound.exception: not_found_exception_handler,
    WerkzeugBadRequest: request_validation_exception_handler,
}
