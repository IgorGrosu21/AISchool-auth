from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
import uvicorn

from core import middlewareStack
from models import init_db
from routers import main_router
from utils import exception_handlers

app = FastAPI(
    title="FastAPI Auth API",
    description="Authentication API with JWT tokens",
    version="1.0.0",
    on_startup=[init_db],
)

def openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="FastAPI Auth API",
        description="Authentication API with JWT tokens and Swagger UI",
        version="1.0.0",
        routes=app.routes,
    )
    for path in openapi_schema["paths"].values():
        for method_data in path.values():
            if "responses" in method_data and "422" in method_data["responses"]:
                del method_data["responses"]["422"]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = openapi

for exception, handler in exception_handlers.items():
    app.add_exception_handler(exception, handler)

# Add middleware in reverse order (last added = first executed)
for middleware in middlewareStack:
    app.add_middleware(middleware)

# Include auth routes
app.include_router(main_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)