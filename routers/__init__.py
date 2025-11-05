from fastapi import APIRouter
from .auth import router as auth_router
from .refresh import router as refresh_router
from .verify import router as verify_router
from .worker import router as worker_router
from .jwks import router as jwks_router

main_router = APIRouter()
main_router.include_router(auth_router)
main_router.include_router(refresh_router)
main_router.include_router(verify_router)
main_router.include_router(worker_router)
main_router.include_router(jwks_router)

