from fastapi import Depends, Cookie
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.dependencies.auth.internal_functions import (
    _validate_and_decode_token,
    _get_user_from_token,
)
from api.api_v1.dependencies.database.db_helper import db_helper
from api.api_v1.dependencies.database.redis_helper import redis_helper
from api.api_v1.exceptions.http_exceptions import (
    InvalidCredentials,
)
from api.api_v1.utils.database import (
    get_user_by_username_or_email,
)
from api.api_v1.utils.security import verify_password
from core.config import settings
from core.models import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=(
        settings.main_router.prefix
        + settings.v1_router.prefix
        + settings.auth_router.prefix
        + settings.auth_router.login_endpoint_path
    )
)


async def get_and_verify_user_from_form(
    user_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
    session: AsyncSession = Depends(db_helper.get_session),
) -> User:
    user = await get_user_by_username_or_email(
        username=user_data.username,
        email=user_data.username,
        session=session,
    )
    if user is None:
        raise InvalidCredentials()

    if not verify_password(
        password=user_data.password,
        correct_password=user.hashed_password,
    ):
        raise InvalidCredentials()
    return user


async def get_user_from_access_token(
    access_token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(db_helper.get_session),
    cache: Redis = Depends(redis_helper.get_redis),
) -> User:
    return await _get_user_from_token(
        token=access_token,
        token_type=settings.jwt_auth.access_token_type,
        session=session,
        cache=cache,
    )


async def get_user_from_refresh_token(
    refresh_token: str = Cookie(),
    session: AsyncSession = Depends(db_helper.get_session),
    cache: Redis = Depends(redis_helper.get_redis),
) -> User:
    return await _get_user_from_token(
        token=refresh_token,
        token_type=settings.jwt_auth.refresh_token_type,
        session=session,
        cache=cache,
    )


async def get_payload_from_access_token(
    access_token: str = Depends(oauth2_scheme),
    cache: Redis = Depends(redis_helper.get_redis),
) -> dict:
    return await _validate_and_decode_token(
        token=access_token,
        token_type=settings.jwt_auth.access_token_type,
        cache=cache,
    )
