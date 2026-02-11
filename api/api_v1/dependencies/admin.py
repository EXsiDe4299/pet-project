from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.dependencies.auth import (
    GetUserFromAccessToken,
    oauth2_scheme,
)
from api.api_v1.dependencies.database.db_helper import db_helper
from api.api_v1.dependencies.database.redis_helper import redis_helper
from api.api_v1.dependencies.users import (
    GetUserByUsername,
)
from api.api_v1.exceptions.http_exceptions import (
    AdminOrSuperAdminRequired,
    CannotModifySelf,
    SuperAdminCanModifyOnlyAdminsOrUsers,
    AdminCanModifyOnlyUsers,
)
from core.models import User
from core.models.user import Role


class VerifyAdmin:
    def __init__(
        self,
        load_tokens: bool = False,
        load_stories: bool = False,
        load_liked_stories: bool = False,
    ):
        self.get_current_user = GetUserFromAccessToken(
            load_tokens=load_tokens,
            load_stories=load_stories,
            load_liked_stories=load_liked_stories,
        )

    async def __call__(
        self,
        access_token: str = Depends(oauth2_scheme),
        session: AsyncSession = Depends(db_helper.get_session),
        cache: Redis = Depends(redis_helper.get_redis),
    ) -> User:
        current_user = await self.get_current_user(
            access_token=access_token,
            session=session,
            cache=cache,
        )
        if current_user.role not in {Role.ADMIN, Role.SUPER_ADMIN}:
            raise AdminOrSuperAdminRequired()
        return current_user


class ValidateUserModification:
    def __init__(
        self,
        load_target_user_tokens: bool = False,
        load_target_user_stories: bool = False,
        load_target_user_liked_stories: bool = False,
        load_current_user_tokens: bool = False,
        load_current_user_stories: bool = False,
        load_current_user_liked_stories: bool = False,
    ):
        self.get_current_user = VerifyAdmin(
            load_tokens=load_current_user_tokens,
            load_stories=load_current_user_stories,
            load_liked_stories=load_current_user_liked_stories,
        )
        self.get_target_user = GetUserByUsername(
            load_tokens=load_target_user_tokens,
            load_stories=load_target_user_stories,
            load_liked_stories=load_target_user_liked_stories,
        )

    async def __call__(
        self,
        username: str,
        session: AsyncSession = Depends(db_helper.get_session),
        access_token: str = Depends(oauth2_scheme),
        cache: Redis = Depends(redis_helper.get_redis),
    ) -> User:
        current_user = await self.get_current_user(
            access_token=access_token,
            session=session,
            cache=cache,
        )
        target_user = await self.get_target_user(
            username=username,
            session=session,
        )

        if current_user.username == target_user.username:
            raise CannotModifySelf()

        if current_user.role == Role.SUPER_ADMIN:
            if target_user.role == Role.SUPER_ADMIN:
                raise SuperAdminCanModifyOnlyAdminsOrUsers()
        elif current_user.role == Role.ADMIN:
            if target_user.role != Role.USER:
                raise AdminCanModifyOnlyUsers()

        return target_user


verify_admin = VerifyAdmin()

validate_user_modification_with_target_stories = ValidateUserModification(
    load_target_user_stories=True,
)
