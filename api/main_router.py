from fastapi import APIRouter

from api.api_v1.routers.v1_router import api_v1_router

api_router = APIRouter()

api_router.include_router(router=api_v1_router, prefix='/v1')
