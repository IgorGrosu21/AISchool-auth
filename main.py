from fastapi import FastAPI
import uvicorn
from core.database import init_db
from routers import main_router as auth_router

app = FastAPI(
    title="FastAPI Auth API",
    description="Authentication API with JWT tokens",
    version="1.0.0",
    on_startup=[init_db],
)

# Include auth routes
app.include_router(auth_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)