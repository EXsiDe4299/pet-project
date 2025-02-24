import pytest
from httpx import AsyncClient, Cookies
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.utils.database import (
    get_user_by_username_or_email,
    update_forgot_password_token,
)
from api.api_v1.utils.email import fm
from core.config import settings
from core.models import User
from core.models.db_helper import db_helper
from tests.integration.conftest import first_user_data, second_user_data, login_path


@pytest.mark.anyio
async def test_incorrect_content_type(
    async_client: AsyncClient,
    first_user_data: dict,
    registration_path: str,
):
    response = await async_client.post(
        url=registration_path,
        headers={
            "accept": "application/json",
            "Content-Type": "text/html; charset=utf-8",
        },
        data=first_user_data,
    )
    assert response.status_code == 422


@pytest.mark.anyio
class TestRegistration:
    async def test_incorrect_email(
        self,
        async_client: AsyncClient,
        first_user_data: dict,
        headers: dict,
        registration_path: str,
    ):
        response = await async_client.post(
            url=registration_path,
            headers=headers,
            data={
                "username": first_user_data["username"],
                "password": first_user_data["password"],
                "email": "incorrect-email",
            },
        )
        assert response.status_code == 422

    async def test_short_username(
        self,
        async_client: AsyncClient,
        first_user_data: dict,
        headers: dict,
        registration_path: str,
    ):
        response = await async_client.post(
            url=registration_path,
            headers=headers,
            data={
                "username": "u",
                "password": first_user_data["password"],
                "email": first_user_data["email"],
            },
        )
        assert response.status_code == 422

    async def test_short_password(
        self,
        async_client: AsyncClient,
        first_user_data: dict,
        headers: dict,
        registration_path: str,
    ):
        response = await async_client.post(
            url=registration_path,
            headers=headers,
            data={
                "username": first_user_data["username"],
                "password": "p",
                "email": first_user_data["email"],
            },
        )
        assert response.status_code == 422

    async def test_long_username(
        self,
        async_client: AsyncClient,
        first_user_data: dict,
        headers: dict,
        registration_path: str,
    ):
        response = await async_client.post(
            url=registration_path,
            headers=headers,
            data={
                "username": first_user_data["username"] * 21,
                "password": first_user_data["password"],
                "email": first_user_data["email"],
            },
        )
        assert response.status_code == 422

    async def test_long_password(
        self,
        async_client: AsyncClient,
        first_user_data: dict,
        headers: dict,
        registration_path: str,
    ):
        response = await async_client.post(
            url=registration_path,
            headers=headers,
            data={
                "username": first_user_data["username"],
                "password": first_user_data["password"] * 101,
                "email": first_user_data["email"],
            },
        )
        assert response.status_code == 422

    async def test_correct_data(
        self,
        async_client: AsyncClient,
        first_user_data: dict,
        headers: dict,
        registration_path: str,
    ):
        response = await async_client.post(
            url=registration_path,
            headers=headers,
            data=first_user_data,
        )
        assert response.status_code == 201
        assert response.json() == {"status": "success"}

    async def test_correct_data2(
        self,
        async_client: AsyncClient,
        second_user_data: dict,
        headers: dict,
        registration_path: str,
    ):
        response = await async_client.post(
            url=registration_path,
            headers=headers,
            data=second_user_data,
        )
        assert response.status_code == 201
        assert response.json() == {"status": "success"}

    async def test_same_username(
        self,
        async_client: AsyncClient,
        third_user_data: dict,
        headers: dict,
        registration_path: str,
    ):
        response = await async_client.post(
            url=registration_path,
            headers=headers,
            data=third_user_data,
        )
        assert response.status_code == 201
        assert response.json() == {"status": "success"}

        response = await async_client.post(
            url=registration_path,
            headers=headers,
            data={
                "username": third_user_data["username"],
                "password": "anotherpassword",
                "email": "another_fake_email1@fakedomain.com",
            },
        )
        assert response.status_code == settings.exc.already_registered_exc.status_code
        assert response.json() == {"detail": settings.exc.already_registered_exc.detail}

    async def test_same_email(
        self,
        async_client: AsyncClient,
        fourth_user_data: dict,
        headers: dict,
        registration_path: str,
    ):
        response = await async_client.post(
            url=registration_path,
            headers=headers,
            data=fourth_user_data,
        )
        assert response.status_code == 201
        assert response.json() == {"status": "success"}

        response = await async_client.post(
            url=registration_path,
            headers=headers,
            data={
                "username": "anotherusername",
                "password": "anotherpassword",
                "email": fourth_user_data["email"],
            },
        )
        assert response.status_code == settings.exc.already_registered_exc.status_code
        assert response.json() == {"detail": settings.exc.already_registered_exc.detail}


@pytest.mark.anyio
class TestSendEmailVerificationToken:
    async def test_incorrect_username_or_email(
        self,
        async_client: AsyncClient,
        first_user_data: dict,
        headers: dict,
        send_email_token_path: str,
    ):
        fm.config.SUPPRESS_SEND = 1
        with fm.record_messages() as outbox:
            response = await async_client.post(
                url=send_email_token_path,
                headers=headers,
                data={
                    "username_or_email": "incorrectusername",
                    "password": first_user_data["password"],
                },
            )
            assert response.status_code == 401
            assert response.json() == {"detail": settings.exc.auth_exc.detail}
            assert len(outbox) == 0

    async def test_incorrect_password(
        self,
        async_client: AsyncClient,
        first_user_data: dict,
        headers: dict,
        send_email_token_path: str,
    ):
        fm.config.SUPPRESS_SEND = 1
        with fm.record_messages() as outbox:
            response = await async_client.post(
                url=send_email_token_path,
                headers=headers,
                data={
                    "username_or_email": first_user_data["username"],
                    "password": "incorrectpassword",
                },
            )
            assert response.status_code == 401
            assert response.json() == {"detail": settings.exc.auth_exc.detail}
            assert len(outbox) == 0

    async def test_correct_data(
        self,
        async_client: AsyncClient,
        first_user_data: dict,
        headers: dict,
        send_email_token_path: str,
    ):
        fm.config.SUPPRESS_SEND = 1
        with fm.record_messages() as outbox:
            response = await async_client.post(
                url=send_email_token_path,
                headers=headers,
                data={
                    "username_or_email": first_user_data["username"],
                    "password": first_user_data["password"],
                },
            )
            assert response.status_code == 200
            assert response.json() == {"status": "success"}
            assert len(outbox) == 1

    async def test_two_same_requests(
        self,
        async_client: AsyncClient,
        second_user_data: dict,
        headers: dict,
        send_email_token_path: str,
    ):
        fm.config.SUPPRESS_SEND = 2
        with fm.record_messages() as outbox:
            for _ in range(2):
                response = await async_client.post(
                    url=send_email_token_path,
                    headers=headers,
                    data={
                        "username_or_email": second_user_data["email"],
                        "password": second_user_data["password"],
                    },
                )
                assert response.status_code == 200
                assert response.json() == {"status": "success"}
            assert len(outbox) == 2


@pytest.mark.anyio
class TestConfirmEmail:
    async def test_invalid_email_token(
        self,
        async_client: AsyncClient,
        headers: dict,
        confirm_email_path: str,
    ):
        response = await async_client.post(
            url=confirm_email_path,
            headers=headers,
            data={"email_verification_token": "invalidtoken"},
        )
        assert response.status_code == settings.exc.invalid_code_exc.status_code
        assert response.json() == {"detail": settings.exc.invalid_code_exc.detail}

    async def test_valid_email_token(
        self,
        async_client: AsyncClient,
        headers: dict,
        first_user_data: dict,
        confirm_email_path: str,
    ):
        session: AsyncSession = await anext(db_helper.get_session())
        user: User = await get_user_by_username_or_email(
            username=first_user_data["username"],
            session=session,
        )
        await session.close()
        email_token: str = user.tokens.email_verification_token
        response = await async_client.post(
            url=confirm_email_path,
            headers=headers,
            data={"email_verification_token": email_token},
        )
        assert response.status_code == 200
        assert response.json() == {"status": "success"}

    async def test_two_same_requests(
        self,
        async_client: AsyncClient,
        headers: dict,
        second_user_data: dict,
        confirm_email_path: str,
    ):
        session: AsyncSession = await anext(db_helper.get_session())
        user: User = await get_user_by_username_or_email(
            username=second_user_data["username"],
            session=session,
        )
        await session.close()
        email_token: str = user.tokens.email_verification_token
        data = {"email_verification_token": email_token}

        response = await async_client.post(
            url=confirm_email_path,
            headers=headers,
            data=data,
        )
        assert response.status_code == 200
        assert response.json() == {"status": "success"}

        response = await async_client.post(
            url=confirm_email_path,
            headers=headers,
            data=data,
        )
        assert response.status_code == settings.exc.invalid_code_exc.status_code
        assert response.json() == {"detail": settings.exc.invalid_code_exc.detail}


@pytest.mark.anyio
class TestForgotPassword:
    async def test_invalid_email(
        self,
        async_client: AsyncClient,
        headers: dict,
        forgot_password_path: str,
    ):
        fm.config.SUPPRESS_SEND = 1
        with fm.record_messages() as outbox:
            response = await async_client.post(
                url=forgot_password_path,
                headers=headers,
                data={"email": "invalid@email.com"},
            )
            assert response.status_code == settings.exc.invalid_email_exc.status_code
            assert response.json() == {"detail": settings.exc.invalid_email_exc.detail}
            assert len(outbox) == 0

    async def test_unconfirmed_email(
        self,
        async_client: AsyncClient,
        headers: dict,
        third_user_data: dict,
        forgot_password_path: str,
    ):
        fm.config.SUPPRESS_SEND = 1
        with fm.record_messages() as outbox:
            response = await async_client.post(
                url=forgot_password_path,
                headers=headers,
                data={"email": third_user_data["email"]},
            )
            assert response.status_code == settings.exc.invalid_email_exc.status_code
            assert response.json() == {"detail": settings.exc.invalid_email_exc.detail}
            assert len(outbox) == 0

    async def test_valid_email(
        self,
        async_client: AsyncClient,
        headers: dict,
        first_user_data: dict,
        forgot_password_path: str,
    ):
        fm.config.SUPPRESS_SEND = 1
        with fm.record_messages() as outbox:
            response = await async_client.post(
                url=forgot_password_path,
                headers=headers,
                data={"email": first_user_data["email"]},
            )
            assert response.status_code == 200
            assert response.json() == {"status": "success"}
            assert len(outbox) == 1


@pytest.mark.anyio
class TestChangePassword:
    async def test_invalid_code(
        self,
        async_client: AsyncClient,
        headers: dict,
        change_password_path: str,
    ):
        response = await async_client.post(
            url=change_password_path,
            headers=headers,
            data={
                "new_password": "newpassword",
                "forgot_password_token": "invalidtoken",
            },
        )
        assert response.status_code == settings.exc.invalid_code_exc.status_code
        assert response.json() == {"detail": settings.exc.invalid_code_exc.detail}

    async def test_short_password(
        self,
        async_client: AsyncClient,
        headers: dict,
        first_user_data: dict,
        change_password_path: str,
    ):
        session: AsyncSession = await anext(db_helper.get_session())
        user: User = await get_user_by_username_or_email(
            username=first_user_data["username"], session=session
        )
        await update_forgot_password_token(
            user_tokens=user.tokens,
            forgot_password_token="qwerty",
            session=session,
        )
        await session.close()
        response = await async_client.post(
            url=change_password_path,
            headers=headers,
            data={
                "new_password": "q",
                "forgot_password_token": "qwerty",
            },
        )
        assert response.status_code == 422

    async def test_long_password(
        self,
        async_client: AsyncClient,
        headers: dict,
        first_user_data: dict,
        change_password_path: str,
    ):
        session: AsyncSession = await anext(db_helper.get_session())
        user: User = await get_user_by_username_or_email(
            username=first_user_data["username"], session=session
        )
        await update_forgot_password_token(
            user_tokens=user.tokens,
            forgot_password_token="qwerty",
            session=session,
        )
        await session.close()
        response = await async_client.post(
            url=change_password_path,
            headers=headers,
            data={
                "new_password": "newpassword" * 101,
                "forgot_password_token": "qwerty",
            },
        )
        assert response.status_code == 422

    async def test_valid_code(
        self,
        async_client: AsyncClient,
        headers: dict,
        first_user_data: dict,
        change_password_path: str,
    ):
        session: AsyncSession = await anext(db_helper.get_session())
        user: User = await get_user_by_username_or_email(
            username=first_user_data["username"], session=session
        )
        await update_forgot_password_token(
            user_tokens=user.tokens,
            forgot_password_token="qwerty",
            session=session,
        )
        await session.close()
        response = await async_client.post(
            url=change_password_path,
            headers=headers,
            data={
                "new_password": "newpassword",
                "forgot_password_token": "qwerty",
            },
        )
        assert response.status_code == 200
        assert response.json() == {"status": "success"}


@pytest.mark.anyio
class TestLogin:
    async def test_invalid_login(
        self,
        async_client: AsyncClient,
        headers: dict,
        second_user_data: dict,
        login_path: str,
    ):
        response = await async_client.post(
            url=login_path,
            headers=headers,
            data={"username_or_email": second_user_data["email"], "password": "asdf"},
        )
        assert response.status_code == settings.exc.auth_exc.status_code
        assert response.json() == {"detail": settings.exc.auth_exc.detail}

    async def test_invalid_password(
        self,
        async_client: AsyncClient,
        headers: dict,
        second_user_data: dict,
        login_path: str,
    ):
        response = await async_client.post(
            url=login_path,
            headers=headers,
            data={
                "username_or_email": "qwer",
                "password": second_user_data["password"],
            },
        )
        assert response.status_code == settings.exc.auth_exc.status_code
        assert response.json() == {"detail": settings.exc.auth_exc.detail}

    async def test_unconfirmed_email(
        self,
        async_client: AsyncClient,
        headers: dict,
        third_user_data: dict,
        login_path: str,
    ):
        response = await async_client.post(
            url=login_path,
            headers=headers,
            data={
                "username_or_email": third_user_data["email"],
                "password": third_user_data["password"],
            },
        )
        assert response.status_code == settings.exc.invalid_email_exc.status_code
        assert response.json() == {"detail": settings.exc.invalid_email_exc.detail}

    async def test_correct_data(
        self,
        async_client: AsyncClient,
        headers: dict,
        second_user_data: dict,
        login_path: str,
    ):
        response = await async_client.post(
            url=login_path,
            headers=headers,
            data={
                "username_or_email": second_user_data["email"],
                "password": second_user_data["password"],
            },
        )
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert "access_token" in response.json().keys()
        assert "refresh_token" in response.json().keys()
        assert response.json()["token_type"] == "Bearer"


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.anyio
class TestRefresh:
    async def test_incorrect_token(
        self,
        async_client: AsyncClient,
        refresh_path: str,
    ):
        response = await async_client.post(
            url=refresh_path,
            cookies=Cookies({"refresh_token": "incorrect-token"}),
        )
        assert response.status_code == 401
        assert response.json() == {"detail": settings.exc.invalid_token_exc.detail}

    async def test_incorrect_token_type(
        self,
        async_client: AsyncClient,
        headers: dict,
        refresh_path: str,
        login_path: str,
        second_user_data: dict,
    ):
        login_response = await async_client.post(
            url=login_path,
            headers=headers,
            data={
                "username_or_email": second_user_data["username"],
                "password": second_user_data["password"],
            },
        )
        access_token = login_response.json()["access_token"]
        response = await async_client.post(
            url=refresh_path,
            cookies=Cookies({"refresh_token": access_token}),
        )
        assert response.status_code == settings.exc.invalid_token_type_exc.status_code
        assert response.json() == {"detail": settings.exc.invalid_token_type_exc.detail}

    async def test_correct_token(
        self,
        async_client: AsyncClient,
        headers: dict,
        refresh_path: str,
        login_path: str,
        second_user_data: dict,
    ):
        login_response = await async_client.post(
            url=login_path,
            headers=headers,
            data={
                "username_or_email": second_user_data["username"],
                "password": second_user_data["password"],
            },
        )
        login_cookies = login_response.cookies
        response = await async_client.post(
            url=refresh_path,
            cookies=login_cookies,
        )
        assert response.status_code == 200
        assert "refresh_token" in response.json().keys()


@pytest.mark.anyio
class TestLogout:
    async def test_logout(
        self,
        async_client: AsyncClient,
        logout_path: str,
    ):
        response = await async_client.get(url=logout_path)
        assert response.status_code == 200
        assert response.json() == {"status": "success"}
        assert response.cookies == Cookies(None)
