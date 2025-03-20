from pathlib import Path

import aiofiles
import aiofiles.os
from fastapi import UploadFile, File, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.exceptions.http_exceptions import (
    InvalidAvatarFormat,
    InvalidAvatarSize,
    UserNotFound,
    AvatarNotFound,
    UnsupportedAvatarExtension,
)
from api.api_v1.utils.database import get_user_by_username_or_email
from api.api_v1.utils.security import validate_avatar_extension, validate_avatar_size
from core.config import settings
from core.models import User
from core.models.db_helper import db_helper


def validate_avatar_dependency(
    avatar: UploadFile | None = File(default=None),
) -> UploadFile | None:
    if avatar:
        if not validate_avatar_extension(avatar=avatar):
            raise InvalidAvatarFormat()
        if not validate_avatar_size(avatar=avatar):
            raise InvalidAvatarSize()
    return avatar


async def get_avatar_path_dependency(
    username: str,
    session: AsyncSession = Depends(db_helper.get_session),
) -> Path:
    user = await get_user_by_username_or_email(username=username, session=session)
    if not user:
        raise UserNotFound()
    if not user.avatar_name:
        raise AvatarNotFound()

    avatar_path = settings.avatar.avatars_dir / user.avatar_name
    if not await aiofiles.os.path.exists(avatar_path):
        raise AvatarNotFound()

    avatar_extension = Path(user.avatar_name).suffix.lower()
    if avatar_extension not in settings.avatar.allowed_extensions_to_mime.keys():
        raise UnsupportedAvatarExtension()
    return avatar_path


async def get_user_by_username_dependency(
    username: str,
    session: AsyncSession = Depends(db_helper.get_session),
) -> User:
    user = await get_user_by_username_or_email(
        username=username,
        session=session,
    )
    if not user:
        raise UserNotFound()
    return user
