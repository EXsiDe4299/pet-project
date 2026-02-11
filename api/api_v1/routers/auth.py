import datetime
import re

from fastapi import APIRouter, Depends, BackgroundTasks, Form
from pydantic import EmailStr
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import Response

from api.api_v1.dependencies.auth import (
    get_user_from_form,
    get_user_from_form_with_tokens,
    get_user_from_refresh_token,
    get_payload_from_access_token,
)
from api.api_v1.dependencies.database.db_helper import db_helper
from api.api_v1.dependencies.database.redis_helper import redis_helper
from api.api_v1.exceptions.http_exceptions import (
    AlreadyRegistered,
    InvalidConfirmEmailCode,
    InvalidEmail,
    InactiveUser,
    InvalidChangePasswordCode,
    EmailAlreadyVerified,
)
from api.api_v1.schemas.auth_responses import (
    StatusSuccessResponse,
    LoginResponse,
    RefreshResponse,
)
from api.api_v1.utils.cache import add_token_to_blacklist
from api.api_v1.utils.database import (
    get_user_by_username_or_email,
    update_user_email_verification_token,
    get_user_by_email_verification_token,
    confirm_user_email,
    update_forgot_password_token,
    create_user_with_tokens,
    get_user_by_forgot_password_token,
    change_user_password,
)
from api.api_v1.utils.email import send_plain_message_to_email
from api.api_v1.utils.jwt_auth import create_access_token, create_refresh_token
from api.api_v1.utils.security import hash_password, generate_email_token
from core.config import settings
from core.models import User

auth_router = APIRouter(
    prefix=settings.auth_router.prefix,
    tags=settings.auth_router.tags,
)


@auth_router.post(
    settings.auth_router.registration_endpoint_path,
    status_code=status.HTTP_201_CREATED,
    response_model=StatusSuccessResponse,
)
async def registration_endpoint(
    username: str = Form(
        default="",
        min_length=3,
        max_length=150,
        pattern=re.compile("[a-zA-Z0-9]+"),  # pyright: ignore
    ),
    email: EmailStr = Form(
        default="",
        max_length=150,
        pattern=re.compile("^\S+@\S+\.\S+$"),  # pyright: ignore
    ),
    password: str = Form(
        default="",
        min_length=6,
        max_length=150,
        pattern=re.compile(
            "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"
        ),  # pyright: ignore
    ),
    session: AsyncSession = Depends(db_helper.get_session),
):
    existing_user = await get_user_by_username_or_email(
        username=username,
        email=email,
        session=session,
    )
    if existing_user:
        raise AlreadyRegistered()

    hashed_password = hash_password(password=password)
    await create_user_with_tokens(
        username=username,
        hashed_password=hashed_password,
        email=email,
        session=session,
    )

    return StatusSuccessResponse()


@auth_router.post(
    settings.auth_router.send_email_token_endpoint_path,
    status_code=status.HTTP_200_OK,
    response_model=StatusSuccessResponse,
)
async def send_email_verification_token_endpoint(
    background_tasks: BackgroundTasks,
    user: User = Depends(get_user_from_form_with_tokens),
    session: AsyncSession = Depends(db_helper.get_session),
):
    if user.is_email_verified:
        raise EmailAlreadyVerified()

    email_verification_token = generate_email_token()

    updated_user = await update_user_email_verification_token(
        user=user,
        email_verification_token=email_verification_token,
        session=session,
    )

    send_plain_message_to_email(
        subject="Email Verification",
        email_address=user.email,
        body=updated_user.tokens.email_verification_token,
        background_tasks=background_tasks,
    )
    return StatusSuccessResponse()


@auth_router.post(
    settings.auth_router.confirm_email_endpoint_path,
    status_code=status.HTTP_200_OK,
    response_model=StatusSuccessResponse,
)
async def confirm_email_endpoint(
    email_verification_token: str = Form(default=""),
    session: AsyncSession = Depends(db_helper.get_session),
):
    email_verification_token = email_verification_token.lower().strip()
    user = await get_user_by_email_verification_token(
        email_verification_token=email_verification_token,
        session=session,
        load_tokens=True,
    )
    if user is None:
        raise InvalidConfirmEmailCode()
    if user.is_email_verified:
        raise EmailAlreadyVerified()

    token_exp = user.tokens.email_verification_token_exp
    if token_exp is None or token_exp < datetime.datetime.now(datetime.UTC):
        raise InvalidConfirmEmailCode()

    await confirm_user_email(
        user=user,
        session=session,
    )

    return StatusSuccessResponse()


@auth_router.post(
    settings.auth_router.forgot_password_endpoint_path,
    status_code=status.HTTP_200_OK,
    response_model=StatusSuccessResponse,
)
async def forgot_password_endpoint(
    background_tasks: BackgroundTasks,
    email: EmailStr = Form(default=""),
    session: AsyncSession = Depends(db_helper.get_session),
):
    user = await get_user_by_username_or_email(
        email=email,
        session=session,
        load_tokens=True,
    )
    if user is None:
        raise InvalidEmail()
    if not user.is_email_verified:
        raise InvalidEmail()
    if not user.is_active:
        raise InactiveUser()

    forgot_password_token = generate_email_token()
    updated_user = await update_forgot_password_token(
        user=user,
        forgot_password_token=forgot_password_token,
        session=session,
    )

    send_plain_message_to_email(
        subject="Resetting password",
        email_address=user.email,
        body=updated_user.tokens.forgot_password_token,
        background_tasks=background_tasks,
    )

    return StatusSuccessResponse()


@auth_router.post(
    settings.auth_router.change_password_endpoint_path,
    status_code=status.HTTP_200_OK,
    response_model=StatusSuccessResponse,
)
async def change_password_endpoint(
    new_password: str = Form(min_length=3, max_length=100, default=""),
    forgot_password_token: str = Form(default=""),
    session: AsyncSession = Depends(db_helper.get_session),
):
    forgot_password_token = forgot_password_token.lower().strip()
    user = await get_user_by_forgot_password_token(
        forgot_password_token=forgot_password_token,
        session=session,
        load_tokens=True,
    )
    if user is None:
        raise InvalidChangePasswordCode()
    if not user.is_email_verified:
        raise InvalidEmail()
    if not user.is_active:
        raise InactiveUser()

    token_exp = user.tokens.forgot_password_token_exp
    if token_exp is None or token_exp < datetime.datetime.now(datetime.UTC):
        raise InvalidChangePasswordCode()

    new_hashed_password = hash_password(password=new_password)
    await change_user_password(
        user=user,
        new_hashed_password=new_hashed_password,
        session=session,
    )
    return StatusSuccessResponse()


@auth_router.post(
    settings.auth_router.login_endpoint_path,
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse,
)
async def login_endpoint(
    response: Response,
    user: User = Depends(get_user_from_form),
):
    if not user.is_active:
        raise InactiveUser()

    if not user.is_email_verified:
        raise InvalidEmail()

    access_token = create_access_token(user=user)
    refresh_token = create_refresh_token(user=user)

    response.set_cookie(
        key=settings.cookie.refresh_token_key,
        value=refresh_token,
        max_age=settings.jwt_auth.refresh_token_expire_minutes * 60,
        expires=settings.jwt_auth.refresh_token_expire_minutes * 60,
        path=settings.cookie.path,
        domain=settings.cookie.domain,
        secure=settings.cookie.secure,
        httponly=settings.cookie.httponly,
        samesite=settings.cookie.samesite,
    )

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@auth_router.post(
    settings.auth_router.refresh_endpoint_path,
    status_code=status.HTTP_200_OK,
    response_model=RefreshResponse,
)
async def refresh_jwt_endpoint(
    response: Response,
    user: User = Depends(get_user_from_refresh_token),
):
    new_access_token = create_access_token(user)
    new_refresh_token = create_refresh_token(user)

    response.set_cookie(
        key=settings.cookie.refresh_token_key,
        value=new_refresh_token,
        max_age=settings.jwt_auth.refresh_token_expire_minutes * 60,
        expires=settings.jwt_auth.refresh_token_expire_minutes * 60,
        path=settings.cookie.path,
        domain=settings.cookie.domain,
        secure=settings.cookie.secure,
        httponly=settings.cookie.httponly,
        samesite=settings.cookie.samesite,
    )

    return RefreshResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
    )


@auth_router.post(
    settings.auth_router.logout_endpoint_path,
    status_code=status.HTTP_200_OK,
    response_model=StatusSuccessResponse,
)
async def logout_endpoint(
    response: Response,
    access_token_payload: dict = Depends(get_payload_from_access_token),
    cache: Redis = Depends(redis_helper.get_redis),
):
    await add_token_to_blacklist(payload=access_token_payload, cache=cache)
    response.delete_cookie(settings.cookie.refresh_token_key)
    return StatusSuccessResponse()
