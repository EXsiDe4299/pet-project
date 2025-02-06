from fastapi import APIRouter

from api.api_v1.routers.v1_router import api_v1_router
from core.config import settings

api_router = APIRouter(prefix=settings.main_router.prefix)

api_router.include_router(router=api_v1_router)
