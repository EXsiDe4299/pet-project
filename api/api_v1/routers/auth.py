import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import Response

from api.api_v1.schemas.auth_responses import (
    LoginResponse,
    LogoutResponse,
    RegistrationResponse,
    RefreshResponse,
)
from api.api_v1.schemas.user import UserRegistrationScheme, UserLoginScheme
from api.api_v1.utils.database import get_user_by_username, create_user
from api.api_v1.dependencies.auth import get_current_user_from_refresh_token
from api.api_v1.utils.jwt_auth import (
    create_access_token,
    create_refresh_token,
)
from api.api_v1.utils.security import (
    hash_password,
    verify_password,
)
from core.config import settings
from core.models import User
from core.models.db_helper import db_helper

auth_router = APIRouter(tags=["Auth"])

logger = logging.getLogger(__name__)


@auth_router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=RegistrationResponse,
)
async def registration_endpoint(
    user_data: UserRegistrationScheme = Depends(UserRegistrationScheme.as_form),
    session: AsyncSession = Depends(db_helper.get_session),
):
    existing_user = await get_user_by_username(
        username=user_data.username,
        session=session,
    )
    if existing_user:
        logger.warning("Registration failed: user already exists")
        raise settings.exc.already_registered_exc

    hashed_password = hash_password(password=user_data.password)
    await create_user(
        username=user_data.username,
        hashed_password=hashed_password,
        session=session,
    )
    logger.info("User registered successfully")
    return RegistrationResponse()


@auth_router.post(
    "/login",
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
    "/refresh",
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
    "/logout",
    status_code=status.HTTP_200_OK,
    response_model=LogoutResponse,
)
async def logout_endpoint(response: Response):
    response.delete_cookie(settings.cookie.refresh_token_key)
    logger.info("Successful logout")
    return LogoutResponse()
