from pathlib import Path

import aiofiles.os
from fastapi import Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.dependencies.database.db_helper import db_helper
from api.api_v1.exceptions.http_exceptions import (
    UserNotFound,
    InvalidAvatarFormat,
    InvalidAvatarSize,
    AvatarNotFound,
    UnsupportedAvatarExtension,
)
from api.api_v1.utils.database import get_user_by_username_or_email
from api.api_v1.utils.security import validate_avatar_extension, validate_avatar_size
from core.config import settings
from core.models import User


class GetUserByUsername:
    def __init__(
        self,
        load_tokens: bool = False,
        load_stories: bool = False,
        load_liked_stories: bool = False,
    ):
        self.load_tokens: bool = load_tokens
        self.load_stories: bool = load_stories
        self.load_liked_stories: bool = load_liked_stories

    async def __call__(
        self,
        username: str,
        session: AsyncSession = Depends(db_helper.get_session),
    ) -> User:
        user = await get_user_by_username_or_email(
            username=username,
            session=session,
            load_tokens=self.load_tokens,
            load_stories=self.load_stories,
            load_liked_stories=self.load_liked_stories,
        )
        if not user:
            raise UserNotFound()
        return user


class GetAvatarPath:
    async def __call__(
        self,
        username: str,
        session: AsyncSession = Depends(db_helper.get_session),
    ) -> Path:
        user = await get_user_by_username_or_email(
            username=username,
            session=session,
            load_tokens=False,
            load_stories=False,
            load_liked_stories=False,
        )

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


class ValidateAvatar:
    async def __call__(
        self,
        avatar: UploadFile | None = File(default=None),
    ) -> UploadFile | None:
        if avatar:
            if not validate_avatar_extension(avatar=avatar):
                raise InvalidAvatarFormat()
            if not await validate_avatar_size(avatar=avatar):
                raise InvalidAvatarSize()
        return avatar


get_user_by_username_with_stories = GetUserByUsername(load_stories=True)

get_avatar_path = GetAvatarPath()

validate_avatar = ValidateAvatar()
