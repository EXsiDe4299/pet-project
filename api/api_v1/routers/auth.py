import logging

from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import Response

from api.api_v1.dependencies.auth import (
    get_current_user_from_refresh_token,
    get_user_registration_data,
    get_user_login_data,
    get_user_during_email_verification,
    get_user_for_resending_email_verification_token,
)
from api.api_v1.schemas.auth_responses import (
    LoginResponse,
    LogoutResponse,
    RegistrationResponse,
    RefreshResponse,
    ConfirmEmailResponse,
    ResendingEmailTokenResponse,
)
from api.api_v1.schemas.user import UserRegistrationScheme
from api.api_v1.utils.database import (
    create_user,
    confirm_user_email,
)
from api.api_v1.utils.email import send_plain_message_to_email
from api.api_v1.utils.jwt_auth import (
    create_access_token,
    create_refresh_token,
)
from api.api_v1.utils.security import (
    hash_password,
    generate_email_verification_token,
)
from core.config import settings
from core.models import User
from core.models.db_helper import db_helper

auth_router = APIRouter(
    prefix=settings.auth_router.prefix,
    tags=settings.auth_router.tags,
)

logger = logging.getLogger(__name__)


@auth_router.post(
    settings.auth_router.registration_endpoint_prefix,
    status_code=status.HTTP_201_CREATED,
    response_model=RegistrationResponse,
)
async def registration_endpoint(
    background_tasks: BackgroundTasks,
    user_data: UserRegistrationScheme = Depends(get_user_registration_data),
    session: AsyncSession = Depends(db_helper.get_session),
):
    hashed_password = hash_password(password=user_data.password)
    email_verification_token = generate_email_verification_token()
    await create_user(
        username=user_data.username,
        hashed_password=hashed_password,
        email=user_data.email,
        email_verification_token=email_verification_token,
        session=session,
    )
    send_plain_message_to_email(
        subject="Email Verification",
        email_address=user_data.email,
        body=email_verification_token,
        background_tasks=background_tasks,
    )

    logger.info("User registered successfully")
    return RegistrationResponse()


@auth_router.post(
    settings.auth_router.login_endpoint_prefix,
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse,
)
async def login_endpoint(
    response: Response,
    user_data: UserLoginScheme = Depends(UserLoginScheme.as_form),
    session: AsyncSession = Depends(db_helper.get_session),
):
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

    access_token = create_access_token(user=user)
    refresh_token = create_refresh_token(user=user)

    response.set_cookie(
        key=settings.cookie.refresh_token_key,
        value=refresh_token,
        max_age=settings.jwt_auth.refresh_token_expire_minutes,
        expires=settings.jwt_auth.refresh_token_expire_minutes,
        path=settings.cookie.path,
        domain=settings.cookie.domain,
        secure=settings.cookie.secure,
        httponly=settings.cookie.httponly,
        samesite=settings.cookie.samesite,
    )

    logger.info("Successful login")
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@auth_router.post(
    settings.auth_router.refresh_endpoint_prefix,
    status_code=status.HTTP_200_OK,
    response_model=RefreshResponse,
)
async def refresh_jwt_endpoint(
    response: Response,
    user: User = Depends(get_current_user_from_refresh_token),
):
    new_access_token = create_access_token(user)
    new_refresh_token = create_refresh_token(user)

    response.set_cookie(
        key=settings.cookie.refresh_token_key,
        value=new_refresh_token,
        max_age=settings.jwt_auth.refresh_token_expire_minutes,
        expires=settings.jwt_auth.refresh_token_expire_minutes,
        path=settings.cookie.path,
        domain=settings.cookie.domain,
        secure=settings.cookie.secure,
        httponly=settings.cookie.httponly,
        samesite=settings.cookie.samesite,
    )

    logger.info("Successful refreshing")
    return RefreshResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
    )


@auth_router.get(
    settings.auth_router.logout_endpoint_prefix,
    status_code=status.HTTP_200_OK,
    response_model=LogoutResponse,
)
async def logout_endpoint(response: Response):
    response.delete_cookie(settings.cookie.refresh_token_key)
    logger.info("Successful logout")
    return LogoutResponse()
