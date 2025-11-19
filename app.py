"""Main application file"""

from flask import Flask, jsonify
from werkzeug.exceptions import BadRequest as WerkzeugBadRequest
from flasgger import Swagger

from core import MIDDLEWARE_STACK
from models import close_db, init_db
from routers import register_blueprints
from schemas import BadRequest, Forbidden, NotFound, Unauthorized

app = Flask(__name__)

# Initialize database
init_db()

# Configure Swagger/OpenAPI
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Flask Auth API",
        "description": "Authentication API with JWT tokens, OAuth2 support, and email verification",
        "version": "1.0.0",
        "contact": {
            "name": "API Support"
        }
    },
    "basePath": "/",
    "schemes": ["http", "https"],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
        }
    },
    "tags": [
        {
            "name": "auth",
            "description": "Authentication endpoints"
        },
        {
            "name": "verify",
            "description": "Email verification endpoints"
        },
        {
            "name": "refresh",
            "description": "Token refresh endpoints"
        },
        {
            "name": "restore",
            "description": "Password restoration endpoints"
        },
        {
            "name": "jwks",
            "description": "JSON Web Key Set endpoints"
        },
        {
            "name": "preview",
            "description": "Email template preview endpoints (debug only)"
        }
    ]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Register teardown handler for database cleanup
app.teardown_appcontext(close_db)

# Register exception handlers
@app.errorhandler(BadRequest.exception)
def bad_request_handler(exc):
    """Handle bad request exceptions"""
    return jsonify({
        "code": exc.status_code,
        "detail": exc.detail,
        "attr": exc.attr
    }), exc.status_code

@app.errorhandler(Unauthorized.exception)
def unauthorized_handler(exc):
    """Handle unauthorized exceptions"""
    return jsonify({
        "code": exc.status_code,
        "detail": exc.detail,
        "attr": exc.attr
    }), exc.status_code

@app.errorhandler(Forbidden.exception)
def forbidden_handler(exc):
    """Handle forbidden exceptions"""
    return jsonify({
        "code": exc.status_code,
        "detail": exc.detail,
        "attr": exc.attr
    }), exc.status_code

@app.errorhandler(NotFound.exception)
def not_found_handler(exc):
    """Handle not found exceptions"""
    return jsonify({
        "code": exc.status_code,
        "detail": exc.detail,
        "attr": exc.attr
    }), exc.status_code

@app.errorhandler(WerkzeugBadRequest)
def werkzeug_bad_request_handler(exc):
    """Handle Werkzeug bad request exceptions"""
    return jsonify({
        "code": 400,
        "detail": getattr(exc, 'description', 'validation_error'),
        "attr": None
    }), 400

# Add middleware in order
# Flask processes before_request in reverse order of registration
# and after_request in order of registration
middleware_instances = []
for middleware_class in reversed(MIDDLEWARE_STACK):
    middleware = middleware_class()
    middleware_instances.append(middleware)
    app.before_request(middleware.before_request)

for middleware in middleware_instances:
    app.after_request(middleware.after_request)

# Register blueprints
register_blueprints(app)
