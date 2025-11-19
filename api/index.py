"""
Vercel serverless handler for FastAPI application
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import FastAPI app
from main import app

# Vercel automatically handles ASGI apps
# Just export the app instance
__all__ = ["app"]

