import asyncio
from asyncio import AbstractEventLoop

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.utils.security import hash_password
from core.config import settings
from core.models import User, Token
from core.models.db_helper import db_helper


@pytest.fixture(scope="session")
def event_loop(request) -> AbstractEventLoop:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture()
def first_user() -> User:
    return User(
        email="first_user_email@email.com",
        username="first_user_name",
        hashed_password=hash_password("password"),
        is_active=True,
        is_email_verified=False,
        tokens=Token(
            email="first_user_email@email.com",
            email_verification_token="qwerty",
            forgot_password_token="123456",
        ),
    )


@pytest.fixture()
def second_user() -> User:
    return User(
        email="second_user_email@email.com",
        username="second_user_name",
        hashed_password=hash_password("password"),
        is_active=True,
        is_email_verified=False,
        tokens=Token(
            email="second_user_email@email.com",
            email_verification_token="asdfgh",
            forgot_password_token="zxcvbn",
        ),
    )


@pytest.fixture()
def token_data() -> dict[str, str]:
    return {
        "sub": "some_email_address@email.com",
        "username": "username",
        settings.jwt_auth.token_type_payload_key: "some_token_type",
    }


@pytest.fixture()
async def session() -> AsyncSession:
    s = await anext(db_helper.get_session())
    yield s
    await s.close()
