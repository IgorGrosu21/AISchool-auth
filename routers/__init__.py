from flask import Flask
from .auth import router as auth_router
from .restore import router as restore_router
from .refresh import router as refresh_router
from .verify import router as verify_router
from .jwks import router as jwks_router
from .preview import router as preview_router

def register_blueprints(app: Flask):
    """Register all blueprints with the Flask app"""
    app.register_blueprint(auth_router)
    app.register_blueprint(restore_router)
    app.register_blueprint(refresh_router)
    app.register_blueprint(verify_router)
    app.register_blueprint(jwks_router)
    app.register_blueprint(preview_router)
