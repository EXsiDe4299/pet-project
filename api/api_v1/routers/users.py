from pathlib import Path

from fastapi import APIRouter, Depends, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import FileResponse

from api.api_v1.dependencies.auth import (
    get_user_from_access_token_with_liked_stories,
    get_user_from_access_token_with_stories,
)
from api.api_v1.dependencies.database.db_helper import db_helper
from api.api_v1.dependencies.users import (
    get_user_by_username_with_stories,
    get_avatar_path,
    validate_avatar,
)
from api.api_v1.exceptions.http_exceptions import InvalidAvatarFormat
from api.api_v1.schemas.story import StoryScheme
from api.api_v1.schemas.user import UserWithStoriesScheme, CurrentUserScheme
from api.api_v1.utils.database import update_user
from api.api_v1.utils.files import save_avatar, delete_avatar
from core.config import settings
from core.models import User

users_router = APIRouter(
    prefix=settings.users_router.prefix,
    tags=settings.users_router.tags,
)


@users_router.get(
    settings.users_router.get_profile_endpoint_path,
    response_model=CurrentUserScheme,
    status_code=status.HTTP_200_OK,
)
async def get_profile_endpoint(
    user: User = Depends(get_user_from_access_token_with_stories),
):
    return user


@users_router.get(
    settings.users_router.get_liked_stories_endpoint_path,
    response_model=list[StoryScheme],
    status_code=status.HTTP_200_OK,
)
async def get_liked_stories_endpoint(
    user: User = Depends(get_user_from_access_token_with_liked_stories),
):
    return user.liked_stories


@users_router.get(
    settings.users_router.get_user_endpoint_path,
    response_model=UserWithStoriesScheme,
    status_code=status.HTTP_200_OK,
)
async def get_user_endpoint(
    user: User = Depends(get_user_by_username_with_stories),
):
    return user


@users_router.patch(
    settings.users_router.edit_profile_endpoint_path,
    response_model=CurrentUserScheme,
    status_code=status.HTTP_200_OK,
)
async def edit_profile_endpoint(
    avatar: UploadFile | None = Depends(validate_avatar),
    bio: str | None = Form(default=None),
    user: User = Depends(get_user_from_access_token_with_stories),
    session: AsyncSession = Depends(db_helper.get_session),
):
    new_avatar_name = None

    if avatar:
        new_avatar_name = await save_avatar(
            avatar=avatar,
            username=user.username,
        )

        if avatar.filename is None:
            raise InvalidAvatarFormat()

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
async def get_avatar_endpoint(avatar_path: Path = Depends(get_avatar_path)):
    avatar_extension = Path(avatar_path).suffix.lower()
    media_type = settings.avatar.allowed_extensions_to_mime[avatar_extension]
    return FileResponse(avatar_path, media_type=media_type)
