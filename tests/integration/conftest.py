import asyncio
from asyncio import AbstractEventLoop
from typing import Generator

import pytest
from httpx import ASGITransport, AsyncClient

from core.config import settings
from main import app


@pytest.fixture(scope="session")
def base_url() -> str:
    return (
        "http://"
        + settings.run.host
        + ":"
        + str(settings.run.port)
        + settings.main_router.prefix
        + settings.v1_router.prefix
    )


@pytest.fixture()
def registration_path() -> str:
    return settings.auth_router.prefix + settings.auth_router.registration_endpoint_path


@pytest.fixture()
def send_email_token_path() -> str:
    return (
        settings.auth_router.prefix
        + settings.auth_router.send_email_token_endpoint_path
    )


@pytest.fixture()
def confirm_email_path() -> str:
    return (
        settings.auth_router.prefix + settings.auth_router.confirm_email_endpoint_path
    )


@pytest.fixture()
def forgot_password_path() -> str:
    return (
        settings.auth_router.prefix + settings.auth_router.forgot_password_endpoint_path
    )


@pytest.fixture()
def change_password_path() -> str:
    return (
        settings.auth_router.prefix + settings.auth_router.change_password_endpoint_path
    )


@pytest.fixture()
def login_path() -> str:
    return settings.auth_router.prefix + settings.auth_router.login_endpoint_path


@pytest.fixture()
def refresh_path() -> str:
    return settings.auth_router.prefix + settings.auth_router.refresh_endpoint_path


@pytest.fixture()
def logout_path() -> str:
    return settings.auth_router.prefix + settings.auth_router.logout_endpoint_path


@pytest.fixture(scope="session")
async def async_client(base_url: str) -> Generator:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=base_url
    ) as client:
        yield client


@pytest.fixture(scope="session")
def event_loop(request) -> AbstractEventLoop:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture()
def headers() -> dict[str, str]:
    return {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }


@pytest.fixture()
def first_user_data() -> dict[str, str]:
    return {
        "username": "first",
        "password": "firstpassword",
        "email": "first_fake_email@fakedomain.com",
    }


@pytest.fixture()
def second_user_data() -> dict[str, str]:
    return {
        "username": "second",
        "password": "secondpassword",
        "email": "second_fake_email@fakedomain.com",
    }


@pytest.fixture()
def third_user_data() -> dict[str, str]:
    return {
        "username": "third",
        "password": "thirdpassword",
        "email": "third_fake_email@fakedomain.com",
    }


@pytest.fixture()
def fourth_user_data() -> dict[str, str]:
    return {
        "username": "fourth",
        "password": "fourthpassword",
        "email": "fourth_fake_email@fakedomain.com",
    }


@pytest.fixture()
def story_data() -> dict[str, str]:
    return {
        "name": "story name",
        "text": "story text",
    }
