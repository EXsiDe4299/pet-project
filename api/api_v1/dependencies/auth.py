import logging

from fastapi import Depends, Cookie
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.schemas.user import UserRegistrationScheme, UserLoginScheme
from api.api_v1.utils.database import (
    get_user_by_username,
    get_user_by_email_verification_token,
    get_user_by_username_or_email,
)
from api.api_v1.utils.jwt_auth import decode_jwt
from api.api_v1.utils.security import validate_token_type, verify_password
from core.config import settings
from core.models import User
from core.models.db_helper import db_helper

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=(
        settings.main_router.prefix
        + settings.v1_router.prefix
        + settings.auth_router.prefix
        + settings.auth_router.login_endpoint_prefix
    )
)

logger = logging.getLogger(__name__)


async def __get_user_from_token(
    *,
    token: str,
    token_type: str,
    session: AsyncSession,
) -> User:
    token_payload = decode_jwt(token=token)
    if not validate_token_type(token_payload=token_payload, expected_type=token_type):
        logger.warning("Refreshing failed: invalid token type")
        raise settings.exc.invalid_token_type_exc

    username = token_payload.get("sub")
    user = await get_user_by_username(username=username, session=session)
    if user is None:
        logger.warning("Refreshing failed: invalid token")
        raise settings.exc.invalid_token_exc

    if not user.is_active:
        logger.warning("Refreshing failed: inactive user")
        raise settings.exc.inactive_user_exc
    if not user.is_email_verified:
        logger.warning("Refreshing failed: email not verified")
        raise settings.exc.not_verified_email_exc

    return user


async def get_current_user_from_access_token(
    access_token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(db_helper.get_session),
) -> User:
    return await __get_user_from_token(
        token=access_token,
        token_type=settings.jwt_auth.access_token_type,
        session=session,
    )


async def get_current_user_from_refresh_token(
    refresh_token: str = Cookie(),
    session: AsyncSession = Depends(db_helper.get_session),
) -> User:
    return await __get_user_from_token(
        token=refresh_token,
        token_type=settings.jwt_auth.refresh_token_type,
        session=session,
    )


async def get_user_registration_data(
    user_data: UserRegistrationScheme = Depends(UserRegistrationScheme.as_form),
    session: AsyncSession = Depends(db_helper.get_session),
) -> UserRegistrationScheme:
    existing_user = await get_user_by_username_or_email(
        username=user_data.username,
        email=user_data.email,
        session=session,
    )
    if existing_user:
        logger.warning("Registration failed: user already exists")
        raise settings.exc.already_registered_exc
    return user_data




async def get_user_login_data(
    user_data: UserLoginScheme = Depends(UserLoginScheme.as_form),
    session: AsyncSession = Depends(db_helper.get_session),
) -> User:
    user = await get_user_by_username(
        username=user_data.username,
        session=session,
    )
    if user is None:
        logger.warning("Login failed: incorrect login or password")
        raise settings.exc.auth_exc

    if not verify_password(
        password=user_data.password, correct_password=user.hashed_password
    ):
        logger.warning("Login failed: incorrect login or password")
        raise settings.exc.auth_exc

    if not user.is_active:
        logger.warning("Login failed: inactive user")
        raise settings.exc.inactive_user_exc

    if not user.is_email_verified:
        logger.warning("Login failed: email not verified")
        raise settings.exc.not_verified_email_exc

    return user
