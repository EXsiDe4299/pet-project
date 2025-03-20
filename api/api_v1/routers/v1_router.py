from fastapi import APIRouter

from api.api_v1.routers.auth import auth_router
from api.api_v1.routers.stories import stories_router
from api.api_v1.routers.users import users_router
from core.config import settings

api_v1_router = APIRouter(prefix=settings.v1_router.prefix)

api_v1_router.include_router(router=auth_router)
api_v1_router.include_router(router=stories_router)
api_v1_router.include_router(router=users_router)
