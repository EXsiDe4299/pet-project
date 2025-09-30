from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.api_v1.dependencies.admin import (
    verify_admin_dependency,
    validate_user_modification_dependency,
)
from api.api_v1.dependencies.db_helper import db_helper
from api.api_v1.exceptions.http_exceptions import (
    UserAlreadyBlocked,
    UserIsNotBlocked,
)
from api.api_v1.schemas.user import UserScheme
from api.api_v1.utils.database import (
    get_active_users,
    get_inactive_users,
    make_admin,
    demote_admin,
    block_user,
    unblock_user,
)
from core.config import settings
from core.models import User

admin_router = APIRouter(
    prefix=settings.admin_router.prefix,
    tags=settings.admin_router.tags,
)


@admin_router.get(
    settings.admin_router.get_active_users_endpoint_path,
    response_model=list[UserScheme],
    status_code=status.HTTP_200_OK,
)
async def get_active_users_endpoint(
    _: User = Depends(verify_admin_dependency),
    session: AsyncSession = Depends(db_helper.get_session),
    page: int = 1,
):
    users = await get_active_users(
        session=session,
        page=page,
    )
    return users


@admin_router.get(
    settings.admin_router.get_inactive_users_endpoint_path,
    response_model=list[UserScheme],
    status_code=status.HTTP_200_OK,
)
async def get_inactive_users_endpoint(
    _: User = Depends(verify_admin_dependency),
    session: AsyncSession = Depends(db_helper.get_session),
    page: int = 1,
):
    users = await get_inactive_users(
        session=session,
        page=page,
    )
    return users


@admin_router.put(
    settings.admin_router.make_admin_endpoint_path,
    response_model=UserScheme,
    status_code=status.HTTP_200_OK,
)
async def make_admin_endpoint(
    target_user: User = Depends(validate_user_modification_dependency),
    session: AsyncSession = Depends(db_helper.get_session),
):
    new_admin = await make_admin(user=target_user, session=session)
    return new_admin


@admin_router.put(
    settings.admin_router.demote_admin_endpoint_path,
    response_model=UserScheme,
    status_code=status.HTTP_200_OK,
)
async def demote_admin_endpoint(
    target_user: User = Depends(validate_user_modification_dependency),
    session: AsyncSession = Depends(db_helper.get_session),
):
    demoted_admin = await demote_admin(user=target_user, session=session)
    return demoted_admin


@admin_router.put(
    settings.admin_router.block_user_endpoint_path,
    response_model=UserScheme,
    status_code=status.HTTP_200_OK,
)
async def block_user_endpoint(
    target_user: User = Depends(validate_user_modification_dependency),
    session: AsyncSession = Depends(db_helper.get_session),
):
    if not target_user.is_active:
        raise UserAlreadyBlocked()
    blocked_user = await block_user(user=target_user, session=session)
    return blocked_user


@admin_router.put(
    settings.admin_router.unblock_user_endpoint_path,
    response_model=UserScheme,
    status_code=status.HTTP_200_OK,
)
async def unblock_user_endpoint(
    target_user: User = Depends(validate_user_modification_dependency),
    session: AsyncSession = Depends(db_helper.get_session),
):
    if target_user.is_active:
        raise UserIsNotBlocked()
    unblocked_user = await unblock_user(user=target_user, session=session)
    return unblocked_user
