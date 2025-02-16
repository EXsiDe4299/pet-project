import datetime

from fastapi import Depends, Cookie, Form
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.schemas.user import UserRegistrationScheme, UserLoginScheme
from api.api_v1.utils.database import (
    get_user_by_email_verification_token,
    get_user_by_username_or_email,
    get_user_by_forgot_password_token,
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
        + settings.auth_router.login_endpoint_path
    )
)


async def __get_user_from_token(
    *,
    token: str,
    token_type: str,
    session: AsyncSession,
) -> User:
    token_payload = decode_jwt(token=token)
    if not validate_token_type(token_payload=token_payload, expected_type=token_type):
        raise settings.exc.invalid_token_type_exc

    email = token_payload.get("sub")
    user = await get_user_by_username_or_email(email=email, session=session)
    if user is None:
        raise settings.exc.invalid_token_exc

    if not user.is_active:
        raise settings.exc.inactive_user_exc
    if not user.is_email_verified:
        raise settings.exc.invalid_email_exc

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
        raise settings.exc.already_registered_exc
    return user_data


async def get_user_for_email_confirming(
    email_verification_token: str = Form(default=""),
    session: AsyncSession = Depends(db_helper.get_session),
) -> User:
    email_verification_token = email_verification_token.lower()
    user = await get_user_by_email_verification_token(
        email_verification_token=email_verification_token,
        session=session,
    )
    if user is None:
        raise settings.exc.invalid_code_exc
    if user.is_email_verified:
        raise settings.exc.email_already_verified_exc
    if user.tokens.email_verification_token_exp < datetime.datetime.now():
        raise settings.exc.invalid_code_exc

    return user


async def __verify_user(
    user_data: UserLoginScheme = Depends(UserLoginScheme.as_form),
    session: AsyncSession = Depends(db_helper.get_session),
) -> User:
    user = await get_user_by_username_or_email(
        username=user_data.username_or_email,
        email=user_data.username_or_email,
        session=session,
    )
    if user is None:
        raise settings.exc.auth_exc

    if not verify_password(
        password=user_data.password,
        correct_password=user.hashed_password,
    ):
        raise settings.exc.auth_exc
    return user


async def get_user_for_sending_email_verification_token(
    user: User = Depends(__verify_user),
) -> User:
    if user.is_email_verified:
        raise settings.exc.email_already_verified_exc
    return user


async def get_user_login_data(
    user: User = Depends(__verify_user),
) -> User:
    if not user.is_active:
        raise settings.exc.inactive_user_exc

    if not user.is_email_verified:
        raise settings.exc.invalid_email_exc

    return user


async def get_user_for_sending_forgot_password_token(
    email: str = Form(default=""),
    session: AsyncSession = Depends(db_helper.get_session),
) -> User:
    user = await get_user_by_username_or_email(
        email=email,
        session=session,
    )
    if user is None:
        raise settings.exc.invalid_email_exc
    if not user.is_email_verified:
        raise settings.exc.invalid_email_exc
    if not user.is_active:
        raise settings.exc.inactive_user_exc

    return user


async def get_user_for_changing_password(
    forgot_password_token: str = Form(default=""),
    session: AsyncSession = Depends(db_helper.get_session),
) -> User:
    user = await get_user_by_forgot_password_token(
        forgot_password_token=forgot_password_token,
        session=session,
    )
    if user is None:
        raise settings.exc.invalid_code_exc
    if not user.is_email_verified:
        raise settings.exc.invalid_email_exc
    if not user.is_active:
        raise settings.exc.inactive_user_exc
    if user.tokens.forgot_password_token_exp < datetime.datetime.now():
        raise settings.exc.invalid_code_exc

    return user
