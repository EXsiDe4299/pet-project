from fastapi import APIRouter, Depends, BackgroundTasks, Form
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import Response

from api.api_v1.dependencies.auth import (
    get_current_user_from_refresh_token,
    get_user_registration_data,
    get_user_login_data,
    get_user_for_email_confirming,
    get_user_for_sending_email_verification_token,
    get_user_for_sending_forgot_password_token,
    get_user_for_changing_password,
)
from api.api_v1.dependencies.db_helper import db_helper
from api.api_v1.schemas.auth_responses import (
    LoginResponse,
    LogoutResponse,
    RegistrationResponse,
    RefreshResponse,
    ConfirmEmailResponse,
    SendingEmailTokenResponse,
    ResetPasswordResponse,
    ForgotPasswordResponse,
)
from api.api_v1.schemas.user import UserRegistrationScheme
from api.api_v1.utils.database import (
    confirm_user_email,
    update_user_email_verification_token,
    update_forgot_password_token,
    change_user_password,
    create_user_with_tokens,
)
from api.api_v1.utils.email import send_plain_message_to_email
from api.api_v1.utils.jwt_auth import (
    create_access_token,
    create_refresh_token,
)
from api.api_v1.utils.security import (
    hash_password,
    generate_email_token,
)
from core.config import settings
from core.models import User
from core.models.db_helper import db_helper

auth_router = APIRouter(
    prefix=settings.auth_router.prefix,
    tags=settings.auth_router.tags,
)


@auth_router.post(
    settings.auth_router.registration_endpoint_path,
    status_code=status.HTTP_201_CREATED,
    response_model=RegistrationResponse,
)
async def registration_endpoint(
    user_data: UserRegistrationScheme = Depends(get_user_registration_data),
    session: AsyncSession = Depends(db_helper.get_session),
):
    hashed_password = hash_password(password=user_data.password)
    await create_user_with_tokens(
        username=user_data.username,
        hashed_password=hashed_password,
        email=user_data.email,
        session=session,
    )

    return RegistrationResponse()


@auth_router.post(
    settings.auth_router.send_email_token_endpoint_path,
    status_code=status.HTTP_200_OK,
    response_model=SendingEmailTokenResponse,
)
async def send_email_verification_token_endpoint(
    background_tasks: BackgroundTasks,
    user: User = Depends(get_user_for_sending_email_verification_token),
    session: AsyncSession = Depends(db_helper.get_session),
):
    email_verification_token = generate_email_token()

    updated_tokens = await update_user_email_verification_token(
        user_tokens=user.tokens,
        email_verification_token=email_verification_token,
        session=session,
    )

    send_plain_message_to_email(
        subject="Email Verification",
        email_address=user.email,
        body=updated_tokens.email_verification_token,
        background_tasks=background_tasks,
    )
    return SendingEmailTokenResponse()


@auth_router.post(
    settings.auth_router.confirm_email_endpoint_path,
    status_code=status.HTTP_200_OK,
    response_model=ConfirmEmailResponse,
)
async def confirm_email_endpoint(
    user: User = Depends(get_user_for_email_confirming),
    session: AsyncSession = Depends(db_helper.get_session),
):
    await confirm_user_email(
        user=user,
        session=session,
    )

    return ConfirmEmailResponse()


@auth_router.post(
    settings.auth_router.forgot_password_endpoint_path,
    status_code=status.HTTP_200_OK,
    response_model=ForgotPasswordResponse,
)
async def forgot_password_endpoint(
    background_tasks: BackgroundTasks,
    user: User = Depends(get_user_for_sending_forgot_password_token),
    session: AsyncSession = Depends(db_helper.get_session),
):
    forgot_password_token = generate_email_token()
    updated_tokens = await update_forgot_password_token(
        user_tokens=user.tokens,
        forgot_password_token=forgot_password_token,
        session=session,
    )

    send_plain_message_to_email(
        subject="Resetting password",
        email_address=user.email,
        body=updated_tokens.forgot_password_token,
        background_tasks=background_tasks,
    )

    return ForgotPasswordResponse()


@auth_router.post(
    settings.auth_router.change_password_endpoint_path,
    status_code=status.HTTP_200_OK,
    response_model=ResetPasswordResponse,
)
async def change_password_endpoint(
    new_password: str = Form(min_length=3, max_length=100, default=""),
    user: User = Depends(get_user_for_changing_password),
    session: AsyncSession = Depends(db_helper.get_session),
):
    new_hashed_password = hash_password(password=new_password)
    await change_user_password(
        user=user,
        new_hashed_password=new_hashed_password,
        session=session,
    )
    return ResetPasswordResponse()


@auth_router.post(
    settings.auth_router.login_endpoint_path,
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse,
)
async def login_endpoint(
    response: Response,
    user: User = Depends(get_user_login_data),
):
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
    user: User = Depends(get_current_user_from_refresh_token),
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


@auth_router.get(
    settings.auth_router.logout_endpoint_path,
    status_code=status.HTTP_200_OK,
    response_model=LogoutResponse,
)
async def logout_endpoint(response: Response):
    response.delete_cookie(settings.cookie.refresh_token_key)
    return LogoutResponse()
