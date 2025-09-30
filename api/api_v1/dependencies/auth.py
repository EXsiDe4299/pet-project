from fastapi import Depends, Cookie
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.dependencies.db_helper import db_helper
from api.api_v1.dependencies.redis_helper import redis_helper
from api.api_v1.exceptions.http_exceptions import (
    InvalidJWT,
    InvalidJWTType,
    InactiveUser,
    InvalidEmail,
    InvalidCredentials,
)
from api.api_v1.schemas.user import UserLoginScheme
from api.api_v1.utils.cache import is_token_in_blacklist
from api.api_v1.utils.database import (
    get_user_by_username_or_email,
)
from api.api_v1.utils.jwt_auth import decode_jwt
from api.api_v1.utils.security import validate_token_type, verify_password
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


async def _validate_and_decode_token(
    token: str,
    token_type: str,
    cache: Redis,
) -> dict:
    try:
        token_payload = decode_jwt(token=token)
    except InvalidTokenError:
        raise InvalidJWT()
    if not validate_token_type(token_payload=token_payload, expected_type=token_type):
        raise InvalidJWTType()

    jti = token_payload.get("jti")
    if await is_token_in_blacklist(jti=jti, cache=cache):
        raise InvalidJWT()

    return token_payload


async def _get_user_from_token(
    token: str,
    token_type: str,
    session: AsyncSession,
    cache: Redis,
) -> User:
    token_payload = await _validate_and_decode_token(
        token=token,
        token_type=token_type,
        cache=cache,
    )
    email = token_payload.get("sub")
    user = await get_user_by_username_or_email(email=email, session=session)
    if user is None:
        raise InvalidJWT()

    if not user.is_active:
        raise InactiveUser()
    if not user.is_email_verified:
        raise InvalidEmail()

    return user


async def get_and_verify_user_from_form(
    user_data: UserLoginScheme = Depends(UserLoginScheme.as_form),
    session: AsyncSession = Depends(db_helper.get_session),
) -> User:
    user = await get_user_by_username_or_email(
        username=user_data.username_or_email,
        email=user_data.username_or_email,
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


async def get_current_user_from_access_token(
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


async def get_current_user_from_refresh_token(
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
