from fastapi import Depends, Cookie
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jwt import InvalidTokenError
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.dependencies.database.db_helper import db_helper
from api.api_v1.dependencies.database.redis_helper import redis_helper
from api.api_v1.exceptions.http_exceptions import (
    InvalidCredentials,
    InvalidJWT,
    InvalidJWTType,
    InactiveUser,
    InvalidEmail,
)
from api.api_v1.utils.cache import is_token_in_blacklist
from api.api_v1.utils.database import get_user_by_username_or_email
from api.api_v1.utils.jwt_auth import decode_jwt
from api.api_v1.utils.security import verify_password, validate_token_type
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


class GetUserFromForm:
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
        user_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
        session: AsyncSession = Depends(db_helper.get_session),
    ) -> User:
        user = await get_user_by_username_or_email(
            username=user_data.username,
            email=user_data.username,
            session=session,
            load_tokens=self.load_tokens,
            load_stories=self.load_stories,
            load_liked_stories=self.load_liked_stories,
        )
        if user is None:
            raise InvalidCredentials()

        if not verify_password(
            password=user_data.password,
            correct_password=user.hashed_password,
        ):
            raise InvalidCredentials()
        return user


class _GetTokenPayloadBase:
    async def _decode_and_validate_token(
        self,
        token: str,
        token_type: str,
        cache: Redis,
    ) -> dict:
        try:
            token_payload = decode_jwt(token=token)
        except InvalidTokenError:
            raise InvalidJWT()
        if not validate_token_type(
            token_payload=token_payload, expected_type=token_type
        ):
            raise InvalidJWTType()

        jti = token_payload.get("jti")
        if jti is None or await is_token_in_blacklist(jti=jti, cache=cache):
            raise InvalidJWT()

        return token_payload


class GetPayloadFromAccessToken(_GetTokenPayloadBase):
    async def __call__(
        self,
        access_token: str = Depends(oauth2_scheme),
        cache: Redis = Depends(redis_helper.get_redis),
    ) -> dict:
        return await self._decode_and_validate_token(
            token=access_token,
            token_type=settings.jwt_auth.access_token_type,
            cache=cache,
        )


class _GetUserFromTokenBase(_GetTokenPayloadBase):
    def __init__(
        self,
        load_tokens: bool = False,
        load_stories: bool = False,
        load_liked_stories: bool = False,
    ):
        self.load_tokens = load_tokens
        self.load_stories = load_stories
        self.load_liked_stories = load_liked_stories

    async def _get_user_from_token(
        self,
        token: str,
        token_type: str,
        session: AsyncSession,
        cache: Redis,
    ) -> User:
        token_payload = await self._decode_and_validate_token(
            token=token,
            token_type=token_type,
            cache=cache,
        )

        username = token_payload.get("sub")
        if username is None:
            raise InvalidJWT()

        user = await get_user_by_username_or_email(
            username=username,
            session=session,
            load_tokens=self.load_tokens,
            load_stories=self.load_stories,
            load_liked_stories=self.load_liked_stories,
        )
        if user is None:
            raise InvalidJWT()

        if not user.is_active:
            raise InactiveUser()
        if not user.is_email_verified:
            raise InvalidEmail()

        return user


class GetUserFromAccessToken(_GetUserFromTokenBase):
    def __init__(
        self,
        load_tokens: bool = False,
        load_stories: bool = False,
        load_liked_stories: bool = False,
    ):
        super().__init__(
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

        return await self._get_user_from_token(
            token=access_token,
            token_type=settings.jwt_auth.access_token_type,
            session=session,
            cache=cache,
        )


class GetUserFromRefreshToken(_GetUserFromTokenBase):
    def __init__(
        self,
        load_tokens: bool = False,
        load_stories: bool = False,
        load_liked_stories: bool = False,
    ):
        super().__init__(
            load_tokens=load_tokens,
            load_stories=load_stories,
            load_liked_stories=load_liked_stories,
        )

    async def __call__(
        self,
        refresh_token: str = Cookie(),
        session: AsyncSession = Depends(db_helper.get_session),
        cache: Redis = Depends(redis_helper.get_redis),
    ) -> User:
        return await self._get_user_from_token(
            token=refresh_token,
            token_type=settings.jwt_auth.refresh_token_type,
            session=session,
            cache=cache,
        )


get_user_from_form = GetUserFromForm()
get_user_from_form_with_tokens = GetUserFromForm(load_tokens=True)

get_payload_from_access_token = GetPayloadFromAccessToken()

get_user_from_access_token = GetUserFromAccessToken()
get_user_from_access_token_with_stories = GetUserFromAccessToken(
    load_stories=True,
)
get_user_from_access_token_with_liked_stories = GetUserFromAccessToken(
    load_liked_stories=True,
)

get_user_from_refresh_token = GetUserFromRefreshToken()
