from pathlib import Path

from fastapi import APIRouter, Depends, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import FileResponse

from api.api_v1.dependencies.auth import get_current_user_from_access_token
from api.api_v1.dependencies.users import (
    validate_avatar_dependency,
    get_avatar_path_dependency,
    get_user_by_username_dependency,
)
from api.api_v1.schemas.user import UserScheme, UserProfileScheme
from api.api_v1.utils.database import update_user
from api.api_v1.utils.files import save_avatar, delete_avatar
from core.config import settings
from core.models import User
from core.models.db_helper import db_helper

users_router = APIRouter(
    prefix=settings.users_router.prefix,
    tags=settings.users_router.tags,
)


@users_router.get(
    settings.users_router.get_user_endpoint_path,
    response_model=UserScheme,
    status_code=status.HTTP_200_OK,
)
async def get_user_endpoint(user: User = Depends(get_user_by_username_dependency)):
    return user


@users_router.get(
    settings.users_router.get_profile_endpoint_path,
    response_model=UserProfileScheme,
    status_code=status.HTTP_200_OK,
)
async def get_profile_endpoint(user: User = Depends(get_current_user_from_access_token)): # fmt: skip
    return user


@users_router.patch(
    settings.users_router.edit_profile_endpoint_path,
    response_model=UserProfileScheme,
    status_code=status.HTTP_200_OK,
)
async def edit_profile_endpoint(
    avatar: UploadFile | None = Depends(validate_avatar_dependency),
    bio: str | None = Form(default=None),
    user: User = Depends(get_current_user_from_access_token),
    session: AsyncSession = Depends(db_helper.get_session),
):
    new_avatar_name = None

    if avatar:
        new_avatar_name = await save_avatar(
            avatar=avatar,
            username=user.username,
        )

        avatar_extension = Path(avatar.filename).suffix.lower()
        if user.avatar_name and not user.avatar_name.lower().endswith(avatar_extension):
            # если пользователь загружает новый аватар, но не с таким расширением, как его предыдущий, то предыдущий будет удален
            # в ином случае файл будет просто перезаписан
            # я так сделал для того чтобы не накапливались аватары с одинаковыми именами, но разными расширениями
            await delete_avatar(avatar_name=user.avatar_name)

    elif user.avatar_name:
        # если пользователь передал avatar=None, то его старый аватар будет удален
        await delete_avatar(avatar_name=user.avatar_name)

    updated_user = await update_user(
        bio=bio,
        avatar_name=new_avatar_name,
        user=user,
        session=session,
    )

    return updated_user


@users_router.get(
    settings.users_router.get_avatar_endpoint_path,
    status_code=status.HTTP_200_OK,
)
async def get_avatar_endpoint(avatar_path: Path = Depends(get_avatar_path_dependency)):
    avatar_extension = Path(avatar_path).suffix.lower()
    media_type = settings.avatar.allowed_extensions_to_mime[avatar_extension]
    return FileResponse(avatar_path, media_type=media_type)
