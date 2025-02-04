from fastapi import APIRouter

from api.api_v1.routers.auth import auth_router

api_v1_router = APIRouter()

api_v1_router.include_router(
    router=auth_router,
    prefix="/auth",
)
