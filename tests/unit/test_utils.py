import datetime
import uuid
from io import BytesIO
from typing import Any
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from uuid import UUID

import bcrypt
import jwt
import pytest
from PIL import Image
from fastapi import UploadFile
from fastapi_mail import MessageSchema, MessageType
from sqlalchemy import Result
from sqlalchemy.exc import SQLAlchemyError

from api.api_v1.utils.database import (
    get_user_by_username_or_email,
    get_user_by_email_verification_token,
    get_user_by_forgot_password_token,
    update_user_email_verification_token,
    update_forgot_password_token,
    change_user_password,
    confirm_user_email,
    get_stories,
    get_stories_by_name_or_text,
    get_story_by_uuid,
    create_user_with_tokens,
    get_author_stories,
    create_story,
    edit_story,
    delete_story,
    like_story,
    update_user,
    get_active_users,
    get_inactive_users,
    make_admin,
    demote_admin,
    block_user,
    unblock_user,
)
from api.api_v1.utils.email import send_plain_message_to_email
from api.api_v1.utils.files import save_avatar, delete_avatar
from api.api_v1.utils.jwt_auth import (
    encode_jwt,
    decode_jwt,
    create_jwt,
    create_access_token,
    create_refresh_token,
)
from api.api_v1.utils.security import (
    hash_password,
    verify_password,
    validate_token_type,
    generate_email_token,
    validate_avatar_extension,
    validate_avatar_size,
)
from core.config import settings
from core.models import User, Token, Story
from core.models.user import Role


@pytest.mark.anyio
class TestDatabase:
    class TestGetUserByUsernameOrEmail:
        async def test_existent_email_and_username(
            self,
            mock_db_session: AsyncMock,
        ):
            email = "test@example.com"
            username = "username"
            mock_user = User(
                username=username,
                email=email,
            )
            mock_result = MagicMock(spec=Result)
            mock_result.scalar_one_or_none.return_value = mock_user
            mock_db_session.execute.return_value = mock_result

            user = await get_user_by_username_or_email(
                username=username,
                email=email,
                session=mock_db_session,
            )

            mock_db_session.execute.assert_awaited_once()
            assert user == mock_user

        async def test_nonexistent_email_and_username(
            self,
            mock_db_session: AsyncMock,
        ):
            mock_result = MagicMock(spec=Result)
            mock_result.scalar_one_or_none.return_value = None
            mock_db_session.execute.return_value = mock_result

            user = await get_user_by_username_or_email(
                username="nonexistent",
                email="nonexistent@example.com",
                session=mock_db_session,
            )

            mock_db_session.execute.assert_awaited_once()
            assert user is None

        async def test_username_only(
            self,
            mock_db_session: AsyncMock,
        ):
            email = "test@example.com"
            username = "username"
            mock_user = User(
                username=username,
                email=email,
            )
            mock_result = MagicMock(spec=Result)
            mock_result.scalar_one_or_none.return_value = mock_user
            mock_db_session.execute.return_value = mock_result

            user = await get_user_by_username_or_email(
                username=username,
                session=mock_db_session,
            )

            mock_db_session.execute.assert_awaited_once()
            assert user == mock_user

        async def test_email_only(
            self,
            mock_db_session: AsyncMock,
        ):
            email = "test@example.com"
            username = "username"
            mock_user = User(
                username=username,
                email=email,
            )
            mock_result = MagicMock(spec=Result)
            mock_result.scalar_one_or_none.return_value = mock_user
            mock_db_session.execute.return_value = mock_result

            user = await get_user_by_username_or_email(
                email=email,
                session=mock_db_session,
            )

            mock_db_session.execute.assert_awaited_once()
            assert user == mock_user

        async def test_without_email_and_username(
            self,
            mock_db_session: AsyncMock,
        ):
            mock_result = MagicMock(spec=Result)
            mock_result.scalar_one_or_none.return_value = None
            mock_db_session.execute.return_value = mock_result

            user = await get_user_by_username_or_email(session=mock_db_session)

            mock_db_session.execute.assert_awaited_once()
            assert user is None

    class TestGetUserByEmailVerificationToken:
        async def test_existent_token(
            self,
            mock_db_session: AsyncMock,
        ):
            token = "valid_token"
            mock_user = User(
                tokens=Token(
                    email_verification_token=token,
                ),
            )
            mock_result = MagicMock(spec=Result)
            mock_result.scalar_one_or_none.return_value = mock_user
            mock_db_session.execute.return_value = mock_result

            user = await get_user_by_email_verification_token(
                email_verification_token=token,
                session=mock_db_session,
            )

            mock_db_session.execute.assert_awaited_once()
            assert user == mock_user

        async def test_nonexistent_token(
            self,
            mock_db_session: AsyncMock,
        ):
            token = "nonexistent_token"
            mock_result = MagicMock(spec=Result)
            mock_result.scalar_one_or_none.return_value = None
            mock_db_session.execute.return_value = mock_result

            user = await get_user_by_email_verification_token(
                email_verification_token=token,
                session=mock_db_session,
            )

            mock_db_session.execute.assert_awaited_once()
            assert user is None

    class TestGetUserByForgotPasswordToken:
        async def test_existent_token(
            self,
            mock_db_session: AsyncMock,
        ):
            token = "valid_token"
            mock_user = User(
                tokens=Token(
                    forgot_password_token=token,
                ),
            )
            mock_result = MagicMock(spec=Result)
            mock_result.scalar_one_or_none.return_value = mock_user
            mock_db_session.execute.return_value = mock_result

            user = await get_user_by_forgot_password_token(
                forgot_password_token=token,
                session=mock_db_session,
            )

            mock_db_session.execute.assert_awaited_once()
            assert user == mock_user

        async def test_nonexistent_token(
            self,
            mock_db_session: AsyncMock,
        ):
            token = "nonexistent_token"
            mock_result = MagicMock(spec=Result)
            mock_result.scalar_one_or_none.return_value = None
            mock_db_session.execute.return_value = mock_result

            user = await get_user_by_forgot_password_token(
                forgot_password_token=token,
                session=mock_db_session,
            )

            mock_db_session.execute.assert_awaited_once()
            assert user is None

    class TestCreateUserWithTokens:
        async def test_success(
            self,
            mock_db_session: AsyncMock,
        ):
            username = "username"
            hashed_password = b"password"
            email = "test@example.com"

            await create_user_with_tokens(
                email=email,
                username=username,
                hashed_password=hashed_password,
                session=mock_db_session,
            )

            mock_db_session.add.assert_called()
            mock_db_session.commit.assert_awaited_once()
            mock_db_session.rollback.assert_not_awaited()

            added_user = mock_db_session.add.call_args_list[0].args[0]
            added_tokens = mock_db_session.add.call_args_list[1].args[0]

            assert isinstance(added_user, User)
            assert isinstance(added_tokens, Token)
            assert added_user.email == email
            assert added_user.hashed_password == hashed_password
            assert added_user.username == username
            assert added_tokens.email == email

        async def test_with_exception(
            self,
            mock_db_session: AsyncMock,
        ):
            username = "username"
            hashed_password = b"password"
            email = "test@example.com"
            mock_db_session.commit.side_effect = SQLAlchemyError("Test error")

            with pytest.raises(SQLAlchemyError, match="Test error"):
                await create_user_with_tokens(
                    email=email,
                    username=username,
                    hashed_password=hashed_password,
                    session=mock_db_session,
                )

            mock_db_session.add.assert_called()
            mock_db_session.commit.assert_awaited_once()
            mock_db_session.rollback.assert_awaited_once()

    class TestUpdateUserEmailVerificationToken:
        async def test_success(
            self,
            mock_db_session: AsyncMock,
        ):
            user_tokens = Token()
            email_verification_token = "new_email_verification_token"
            expire_minutes = 5

            updated_tokens = await update_user_email_verification_token(
                user_tokens=user_tokens,
                email_verification_token=email_verification_token,
                expire_minutes=expire_minutes,
                session=mock_db_session,
            )

            assert isinstance(updated_tokens, Token)
            assert updated_tokens.email_verification_token == email_verification_token
            expected_expiration = datetime.datetime.now(
                datetime.UTC
            ) + datetime.timedelta(minutes=expire_minutes)
            assert updated_tokens.email_verification_token_exp is not None
            expiration_time_diff = abs(
                (
                    updated_tokens.email_verification_token_exp - expected_expiration
                ).total_seconds()
            )
            assert expiration_time_diff < 10
            mock_db_session.commit.assert_awaited_once()
            mock_db_session.refresh.assert_awaited_once()

        async def test_with_exception(
            self,
            mock_db_session: AsyncMock,
        ):
            user_tokens = Token()
            email_verification_token = "new_email_verification_token"
            expire_minutes = 5
            mock_db_session.commit.side_effect = SQLAlchemyError("Test error")

            with pytest.raises(SQLAlchemyError, match="Test error"):
                await update_user_email_verification_token(
                    user_tokens=user_tokens,
                    email_verification_token=email_verification_token,
                    expire_minutes=expire_minutes,
                    session=mock_db_session,
                )

            mock_db_session.commit.assert_awaited_once()
            mock_db_session.rollback.assert_awaited_once()
            mock_db_session.refresh.assert_not_awaited()

    class TestUpdateForgotPasswordToken:
        async def test_success(
            self,
            mock_db_session: AsyncMock,
        ):
            user_tokens = Token()
            forgot_password_token = "new_forgot_password_token"
            expire_minutes = 5

            updated_tokens = await update_forgot_password_token(
                user_tokens=user_tokens,
                forgot_password_token=forgot_password_token,
                expire_minutes=expire_minutes,
                session=mock_db_session,
            )

            assert isinstance(updated_tokens, Token)
            assert updated_tokens.forgot_password_token == forgot_password_token
            expected_expiration = datetime.datetime.now(
                datetime.UTC
            ) + datetime.timedelta(minutes=expire_minutes)
            assert updated_tokens.forgot_password_token_exp is not None
            expiration_time_diff = abs(
                (
                    updated_tokens.forgot_password_token_exp - expected_expiration
                ).total_seconds()
            )
            assert expiration_time_diff < 10
            mock_db_session.commit.assert_awaited_once()
            mock_db_session.refresh.assert_awaited_once()

        async def test_with_exception(
            self,
            mock_db_session: AsyncMock,
        ):
            user_tokens = Token()
            forgot_password_token = "new_forgot_password_token"
            expire_minutes = 5
            mock_db_session.commit.side_effect = SQLAlchemyError("Test error")

            with pytest.raises(SQLAlchemyError, match="Test error"):
                await update_forgot_password_token(
                    user_tokens=user_tokens,
                    forgot_password_token=forgot_password_token,
                    expire_minutes=expire_minutes,
                    session=mock_db_session,
                )

            mock_db_session.commit.assert_awaited_once()
            mock_db_session.rollback.assert_awaited_once()
            mock_db_session.refresh.assert_not_awaited()

    class TestChangeUserPassword:
        async def test_success(
            self,
            mock_db_session: AsyncMock,
        ):
            hashed_password = b"password"
            new_hashed_password = b"new_password"
            forgot_password_token = "forgot_password_token"
            forgot_password_token_exp = datetime.datetime.now(datetime.UTC)
            mock_user = User(
                hashed_password=hashed_password,
                tokens=Token(
                    forgot_password_token=forgot_password_token,
                    forgot_password_token_exp=forgot_password_token_exp,
                ),
            )

            changed_user = await change_user_password(
                user=mock_user,
                new_hashed_password=new_hashed_password,
                session=mock_db_session,
            )

            assert isinstance(changed_user, User)
            assert changed_user.hashed_password == new_hashed_password
            assert changed_user.tokens.forgot_password_token is None
            assert changed_user.tokens.forgot_password_token_exp is None
            mock_db_session.commit.assert_awaited_once()
            mock_db_session.refresh.assert_awaited_once()
            mock_db_session.rollback.assert_not_awaited()

        async def test_with_exception(
            self,
            mock_db_session: AsyncMock,
        ):
            hashed_password = b"password"
            new_hashed_password = b"new_password"
            forgot_password_token = "forgot_password_token"
            forgot_password_token_exp = datetime.datetime.now(datetime.UTC)
            mock_user = User(
                hashed_password=hashed_password,
                tokens=Token(
                    forgot_password_token=forgot_password_token,
                    forgot_password_token_exp=forgot_password_token_exp,
                ),
            )
            mock_db_session.commit.side_effect = SQLAlchemyError("Test error")

            with pytest.raises(SQLAlchemyError, match="Test error"):
                await change_user_password(
                    user=mock_user,
                    new_hashed_password=new_hashed_password,
                    session=mock_db_session,
                )

            mock_db_session.commit.assert_awaited_once()
            mock_db_session.rollback.assert_awaited_once()
            mock_db_session.refresh.assert_not_awaited()

    class TestConfirmUserEmail:
        async def test_success(
            self,
            mock_db_session: AsyncMock,
        ):
            email_verification_token = "email_verification_token"
            email_verification_token_exp = datetime.datetime.now(datetime.UTC)
            mock_user = User(
                is_email_verified=False,
                tokens=Token(
                    email_verification_token=email_verification_token,
                    email_verification_token_exp=email_verification_token_exp,
                ),
            )

            await confirm_user_email(user=mock_user, session=mock_db_session)

            mock_db_session.commit.assert_awaited_once()
            mock_db_session.rollback.assert_not_awaited()

        async def test_with_exception(
            self,
            mock_db_session: AsyncMock,
        ):
            email_verification_token = "email_verification_token"
            email_verification_token_exp = datetime.datetime.now(datetime.UTC)
            mock_user = User(
                is_email_verified=False,
                tokens=Token(
                    email_verification_token=email_verification_token,
                    email_verification_token_exp=email_verification_token_exp,
                ),
            )
            mock_db_session.commit.side_effect = SQLAlchemyError("Test error")

            with pytest.raises(SQLAlchemyError, match="Test error"):
                await confirm_user_email(user=mock_user, session=mock_db_session)

            mock_db_session.commit.assert_awaited_once()
            mock_db_session.rollback.assert_awaited_once()

    class TestGetStories:
        async def test_some_stories(
            self,
            mock_db_session: AsyncMock,
        ):
            mock_story1 = Story(name="story 1")
            mock_story2 = Story(name="story 2")
            mock_result = MagicMock(spec=Result)
            mock_result.unique.return_value.scalars.return_value.fetchall.return_value = [
                mock_story1,
                mock_story2,
            ]
            mock_db_session.execute.return_value = mock_result

            stories = await get_stories(session=mock_db_session)

            assert len(stories) == 2
            assert stories[0].name == mock_story1.name
            assert stories[1].name == mock_story2.name
            mock_db_session.execute.assert_awaited_once()

        async def test_empty_result(
            self,
            mock_db_session: AsyncMock,
        ):
            mock_result = MagicMock(spec=Result)
            mock_result.unique.return_value.scalars.return_value.fetchall.return_value = (
                []
            )
            mock_db_session.execute.return_value = mock_result

            stories = await get_stories(session=mock_db_session)

            assert len(stories) == 0
            mock_db_session.execute.assert_awaited_once()

    class TestGetStoriesByNameOrText:
        async def test_empty_result(
            self,
            mock_db_session: AsyncMock,
        ):
            mock_result = MagicMock(spec=Result)
            mock_result.unique.return_value.scalars.return_value.fetchall.return_value = (
                []
            )
            mock_db_session.execute.return_value = mock_result

            stories = await get_stories_by_name_or_text(
                query="nonexistent",
                session=mock_db_session,
            )

            assert len(stories) == 0
            mock_db_session.execute.assert_awaited_once()

        async def test_by_name(
            self,
            mock_db_session: AsyncMock,
        ):
            mock_story1 = Story(name="story 1 name")
            mock_story2 = Story(name="story 2 name")
            mock_result = MagicMock(spec=Result)
            mock_result.unique.return_value.scalars.return_value.fetchall.return_value = [
                mock_story1,
                mock_story2,
            ]
            mock_db_session.execute.return_value = mock_result

            stories = await get_stories_by_name_or_text(
                query="story",
                session=mock_db_session,
            )

            assert len(stories) == 2
            assert stories[0].name == mock_story1.name
            assert stories[1].name == mock_story2.name
            mock_db_session.execute.assert_awaited_once()

        async def test_by_text(
            self,
            mock_db_session: AsyncMock,
        ):
            mock_story1 = Story(text="story 1 text")
            mock_story2 = Story(text="story 2 text")
            mock_result = MagicMock(spec=Result)
            mock_result.unique.return_value.scalars.return_value.fetchall.return_value = [
                mock_story1,
                mock_story2,
            ]
            mock_db_session.execute.return_value = mock_result

            stories = await get_stories_by_name_or_text(
                query="story",
                session=mock_db_session,
            )

            assert len(stories) == 2
            assert stories[0].name == mock_story1.name
            assert stories[1].name == mock_story2.name
            mock_db_session.execute.assert_awaited_once()

        async def test_by_name_and_text(
            self,
            mock_db_session: AsyncMock,
        ):
            mock_story1 = Story(name="test story 1 name", text="story 1 text")
            mock_story2 = Story(name="story 2 name", text="test story 2 text")
            mock_story3 = Story(name="story 3 name", text="test story 3 text")
            mock_result = MagicMock(spec=Result)
            mock_result.unique.return_value.scalars.return_value.fetchall.return_value = [
                mock_story1,
                mock_story2,
                mock_story3,
            ]
            mock_db_session.execute.return_value = mock_result

            stories = await get_stories_by_name_or_text(
                query="test",
                session=mock_db_session,
            )

            assert len(stories) == 3
            assert stories[0].name == mock_story1.name
            assert stories[0].text == mock_story1.text
            assert stories[1].name == mock_story2.name
            assert stories[1].text == mock_story2.text
            assert stories[2].name == mock_story3.name
            assert stories[2].text == mock_story3.text
            mock_db_session.execute.assert_awaited_once()

    class TestGetStoryByUuid:
        async def test_success(
            self,
            mock_db_session: AsyncMock,
        ):
            story_id = UUID("59f7c198-c96c-4e32-b09a-665fa84e63fa")
            mock_story = Story(id=story_id)
            mock_result = MagicMock(spec=Result)
            mock_result.unique.return_value.scalar_one_or_none.return_value = mock_story
            mock_db_session.execute.return_value = mock_result

            story = await get_story_by_uuid(
                story_uuid=story_id,
                session=mock_db_session,
            )
            mock_db_session.execute.assert_awaited_once()
            assert story is not None
            assert story.id == story_id

        async def test_not_found(
            self,
            mock_db_session: AsyncMock,
        ):
            story_id = UUID("59f7c198-c96c-4e32-b09a-665fa84e63fa")
            mock_result = MagicMock(spec=Result)
            mock_result.unique.return_value.scalar_one_or_none.return_value = None
            mock_db_session.execute.return_value = mock_result

            story = await get_story_by_uuid(
                story_uuid=story_id,
                session=mock_db_session,
            )
            mock_db_session.execute.assert_awaited_once()
            assert story is None

    class TestGetAuthorStories:
        async def test_success(
            self,
            mock_db_session: AsyncMock,
        ):
            author_email = "test@example.com"
            username = "username"
            author = User(
                email=author_email,
                username=username,
            )
            mock_story1 = Story(
                author_email=author_email,
                author=author,
            )
            mock_story2 = Story(
                author_email=author_email,
                author=author,
            )
            mock_result = MagicMock(spec=Result)
            mock_result.unique.return_value.scalars.return_value.fetchall.return_value = [
                mock_story1,
                mock_story2,
            ]
            mock_db_session.execute.return_value = mock_result

            stories = await get_author_stories(
                author_username=username,
                session=mock_db_session,
            )

            mock_db_session.execute.assert_awaited_once()
            assert len(stories) == 2
            assert stories[0].author_email == author_email
            assert stories[0].author.email == author_email
            assert stories[0].author.username == username
            assert stories[1].author_email == author_email
            assert stories[1].author.email == author_email
            assert stories[1].author.username == username

        async def test_empty_result(
            self,
            mock_db_session: AsyncMock,
        ):
            username = "nonexistent"
            mock_result = MagicMock(spec=Result)
            mock_result.unique.return_value.scalars.return_value.fetchall.return_value = (
                []
            )
            mock_db_session.execute.return_value = mock_result

            stories = await get_author_stories(
                author_username=username,
                session=mock_db_session,
            )

            mock_db_session.execute.assert_awaited_once()
            assert len(stories) == 0

    class TestGetActiveUsers:
        async def test_success(
            self,
            mock_db_session: AsyncMock,
        ):
            mock_user1 = User(
                username="user1",
                is_active=True,
            )
            mock_user2 = User(
                username="user2",
                is_active=True,
            )
            mock_result = MagicMock(spec=Result)
            mock_result.scalars.return_value.fetchall.return_value = [
                mock_user1,
                mock_user2,
            ]
            mock_db_session.execute.return_value = mock_result

            active_users = await get_active_users(
                session=mock_db_session,
            )

            mock_db_session.execute.assert_awaited_once()
            assert len(active_users) == 2
            assert active_users[0].username == "user1"
            assert active_users[0].is_active
            assert active_users[1].username == "user2"
            assert active_users[1].is_active

        async def test_empty_result(
            self,
            mock_db_session: AsyncMock,
        ):
            mock_result = MagicMock(spec=Result)
            mock_result.scalars.return_value.fetchall.return_value = []
            mock_db_session.execute.return_value = mock_result

            active_users = await get_active_users(
                session=mock_db_session,
            )

            mock_db_session.execute.assert_awaited_once()
            assert len(active_users) == 0

    class TestGetInactiveUsers:
        async def test_success(
            self,
            mock_db_session: AsyncMock,
        ):
            mock_user1 = User(
                username="user1",
                is_active=False,
            )
            mock_user2 = User(
                username="user2",
                is_active=False,
            )
            mock_result = MagicMock(spec=Result)
            mock_result.scalars.return_value.fetchall.return_value = [
                mock_user1,
                mock_user2,
            ]
            mock_db_session.execute.return_value = mock_result

            inactive_users = await get_inactive_users(
                session=mock_db_session,
            )

            mock_db_session.execute.assert_awaited_once()
            assert len(inactive_users) == 2
            assert inactive_users[0].username == "user1"
            assert not inactive_users[0].is_active
            assert inactive_users[1].username == "user2"
            assert not inactive_users[1].is_active

        async def test_empty_result(
            self,
            mock_db_session: AsyncMock,
        ):
            mock_result = MagicMock(spec=Result)
            mock_result.scalars.return_value.fetchall.return_value = []
            mock_db_session.execute.return_value = mock_result

            inactive_users = await get_inactive_users(
                session=mock_db_session,
            )

            mock_db_session.execute.assert_awaited_once()
            assert len(inactive_users) == 0

    class TestMakeAdmin:
        async def test_success(
            self,
            mock_db_session: AsyncMock,
        ):
            mock_user = User(role=Role.USER)

            new_admin = await make_admin(
                user=mock_user,
                session=mock_db_session,
            )

            mock_db_session.commit.assert_awaited_once()
            mock_db_session.refresh.assert_awaited_once()
            mock_db_session.rollback.assert_not_awaited()

            assert isinstance(new_admin, User)
            assert new_admin.role == Role.ADMIN

        async def test_with_exception(
            self,
            mock_db_session: AsyncMock,
        ):
            mock_user = User(role=Role.USER)
            mock_db_session.commit.side_effect = SQLAlchemyError("Test error")

            with pytest.raises(SQLAlchemyError, match="Test error"):
                await make_admin(
                    user=mock_user,
                    session=mock_db_session,
                )

            mock_db_session.commit.assert_awaited_once()
            mock_db_session.refresh.assert_not_awaited()
            mock_db_session.rollback.assert_awaited_once()

    class TestDemoteAdmin:
        async def test_success(
            self,
            mock_db_session: AsyncMock,
        ):
            mock_admin = User(role=Role.ADMIN)

            demoted_admin = await demote_admin(
                user=mock_admin,
                session=mock_db_session,
            )

            mock_db_session.commit.assert_awaited_once()
            mock_db_session.refresh.assert_awaited_once()
            mock_db_session.rollback.assert_not_awaited()

            assert isinstance(demoted_admin, User)
            assert demoted_admin.role == Role.USER

        async def test_with_exception(
            self,
            mock_db_session: AsyncMock,
        ):
            mock_admin = User(role=Role.ADMIN)
            mock_db_session.commit.side_effect = SQLAlchemyError("Test error")

            with pytest.raises(SQLAlchemyError, match="Test error"):
                await demote_admin(
                    user=mock_admin,
                    session=mock_db_session,
                )

            mock_db_session.commit.assert_awaited_once()
            mock_db_session.refresh.assert_not_awaited()
            mock_db_session.rollback.assert_awaited_once()

    class TestBlockUser:
        async def test_success(
            self,
            mock_db_session: AsyncMock,
        ):
            mock_user = User(is_active=True)

            blocked_user = await block_user(
                user=mock_user,
                session=mock_db_session,
            )

            mock_db_session.commit.assert_awaited_once()
            mock_db_session.refresh.assert_awaited_once()
            mock_db_session.rollback.assert_not_awaited()

            assert isinstance(blocked_user, User)
            assert not blocked_user.is_active

        async def test_with_exception(
            self,
            mock_db_session: AsyncMock,
        ):
            mock_user = User(is_active=True)
            mock_db_session.commit.side_effect = SQLAlchemyError("Test error")

            with pytest.raises(SQLAlchemyError, match="Test error"):
                await demote_admin(
                    user=mock_user,
                    session=mock_db_session,
                )

            mock_db_session.commit.assert_awaited_once()
            mock_db_session.refresh.assert_not_awaited()
            mock_db_session.rollback.assert_awaited_once()

    class TestUnblockUser:
        async def test_success(
            self,
            mock_db_session: AsyncMock,
        ):
            mock_user = User(is_active=False)

            unblocked_user = await unblock_user(
                user=mock_user,
                session=mock_db_session,
            )

            mock_db_session.commit.assert_awaited_once()
            mock_db_session.refresh.assert_awaited_once()
            mock_db_session.rollback.assert_not_awaited()

            assert isinstance(unblocked_user, User)
            assert unblocked_user.is_active

        async def test_with_exception(
            self,
            mock_db_session: AsyncMock,
        ):
            mock_user = User(is_active=False)
            mock_db_session.commit.side_effect = SQLAlchemyError("Test error")

            with pytest.raises(SQLAlchemyError, match="Test error"):
                await unblock_user(
                    user=mock_user,
                    session=mock_db_session,
                )

            mock_db_session.commit.assert_awaited_once()
            mock_db_session.refresh.assert_not_awaited()
            mock_db_session.rollback.assert_awaited_once()

    class TestCreateStory:
        async def test_success(
            self,
            mock_db_session: AsyncMock,
        ):
            name = "Test story name"
            text = "Test story text"
            author_email = "test@example.com"

            added_story = await create_story(
                name=name,
                text=text,
                author_email=author_email,
                session=mock_db_session,
            )

            mock_db_session.add.assert_called()
            mock_db_session.commit.assert_awaited_once()
            mock_db_session.rollback.assert_not_awaited()

            assert isinstance(added_story, Story)
            assert added_story.name == name
            assert added_story.text == text
            assert added_story.author_email == author_email

        async def test_with_exception(
            self,
            mock_db_session: AsyncMock,
        ):
            name = "Test story name"
            text = "Test story text"
            author_email = "test@example.com"
            mock_db_session.commit.side_effect = SQLAlchemyError("Test error")

            with pytest.raises(SQLAlchemyError, match="Test error"):
                await create_story(
                    name=name,
                    text=text,
                    author_email=author_email,
                    session=mock_db_session,
                )

            mock_db_session.add.assert_called()
            mock_db_session.commit.assert_awaited_once()
            mock_db_session.rollback.assert_awaited_once()

    class TestEditStory:
        async def test_success(
            self,
            mock_db_session: AsyncMock,
        ):
            mock_story = Story(
                name="Test story name",
                text="Test story text",
            )
            new_story_name = "New test story name"
            new_story_text = "New test story text"

            edited_story = await edit_story(
                name=new_story_name,
                text=new_story_text,
                story=mock_story,
                session=mock_db_session,
            )

            mock_db_session.commit.assert_awaited_once()
            mock_db_session.refresh.assert_awaited_once()
            mock_db_session.rollback.assert_not_awaited()

            assert isinstance(edited_story, Story)
            assert edited_story.name == new_story_name
            assert edited_story.text == new_story_text

        async def test_with_exception(
            self,
            mock_db_session: AsyncMock,
        ):
            mock_story = Story(
                name="Test story name",
                text="Test story text",
            )
            new_story_name = "New test story name"
            new_story_text = "New test story text"
            mock_db_session.commit.side_effect = SQLAlchemyError("Test error")

            with pytest.raises(SQLAlchemyError, match="Test error"):
                await edit_story(
                    name=new_story_name,
                    text=new_story_text,
                    story=mock_story,
                    session=mock_db_session,
                )

            mock_db_session.commit.assert_awaited_once()
            mock_db_session.rollback.assert_awaited_once()
            mock_db_session.refresh.assert_not_awaited()

    class TestDeleteStory:
        async def test_success(
            self,
            mock_db_session: AsyncMock,
        ):
            name = "Test story name"
            text = "Test story text"
            mock_story = Story(
                name=name,
                text=text,
            )

            await delete_story(story=mock_story, session=mock_db_session)

            mock_db_session.delete.assert_awaited_once()
            mock_db_session.commit.assert_awaited_once()
            mock_db_session.rollback.assert_not_awaited()

            deleted_story: Story = mock_db_session.delete.call_args[0][0]

            assert deleted_story.name == name
            assert deleted_story.text == text

        async def test_with_exception(
            self,
            mock_db_session: AsyncMock,
        ):
            mock_story = Story(
                name="Test story name",
                text="Test story text",
            )
            mock_db_session.commit.side_effect = SQLAlchemyError("Test error")

            with pytest.raises(SQLAlchemyError, match="Test error"):
                await delete_story(story=mock_story, session=mock_db_session)

            mock_db_session.delete.assert_awaited_once()
            mock_db_session.commit.assert_awaited_once()
            mock_db_session.rollback.assert_awaited_once()

    class TestLikeStory:
        async def test_like(
            self,
            mock_db_session: AsyncMock,
        ):
            username = "username"
            story_name = "Test story name"
            mock_user = User(
                username=username,
                liked_stories=[],
            )
            mock_story = Story(
                name=story_name,
                likes_number=0,
                likers=[],
            )

            await like_story(
                story=mock_story,
                user=mock_user,
                session=mock_db_session,
            )

            mock_db_session.commit.assert_awaited_once()
            mock_db_session.rollback.assert_not_awaited()
            assert mock_story.likes_number == 1
            assert len(mock_story.likers) == 1
            assert mock_story.likers[0].username == mock_user.username
            assert len(mock_user.liked_stories) == 1
            assert mock_user.liked_stories[0].name == story_name

        async def test_unlike(
            self,
            mock_db_session: AsyncMock,
        ):
            username = "username"
            mock_user = User(
                username=username,
            )
            mock_story = Story(
                likes_number=1,
            )
            mock_user.liked_stories = [mock_story]
            mock_story.likers = [mock_user]

            await like_story(
                story=mock_story,
                user=mock_user,
                session=mock_db_session,
            )

            mock_db_session.commit.assert_awaited_once()
            mock_db_session.rollback.assert_not_awaited()
            assert mock_story.likes_number == 0
            assert len(mock_story.likers) == 0
            assert len(mock_user.liked_stories) == 0

        async def test_with_exception(
            self,
            mock_db_session: AsyncMock,
        ):
            username = "username"
            story_name = "Test story name"
            mock_user = User(
                username=username,
                liked_stories=[],
            )
            mock_story = Story(
                name=story_name,
                likes_number=0,
                likers=[],
            )
            mock_db_session.commit.side_effect = SQLAlchemyError("Test error")

            with pytest.raises(SQLAlchemyError, match="Test error"):
                await like_story(
                    story=mock_story,
                    user=mock_user,
                    session=mock_db_session,
                )

            mock_db_session.commit.assert_awaited_once()
            mock_db_session.rollback.assert_awaited_once()

    class TestUpdateUser:
        async def test_success(
            self,
            mock_db_session: AsyncMock,
        ):
            mock_user = User(
                bio="Test biography",
                avatar_name="testavatar.jpg",
            )
            new_bio = "New test biography"
            new_avatar_name = "newtestavatar.jpg"

            updated_user = await update_user(
                bio=new_bio,
                avatar_name=new_avatar_name,
                user=mock_user,
                session=mock_db_session,
            )

            mock_db_session.commit.assert_awaited_once()
            mock_db_session.refresh.assert_awaited_once()
            mock_db_session.rollback.assert_not_awaited()

            assert isinstance(updated_user, User)
            assert updated_user.bio == new_bio
            assert updated_user.avatar_name == new_avatar_name

        async def test_with_exception(
            self,
            mock_db_session: AsyncMock,
        ):
            mock_user = User(
                bio="Test biography",
                avatar_name="testavatar.jpg",
            )
            new_bio = "New test biography"
            new_avatar_name = "newtestavatar.jpg"
            mock_db_session.commit.side_effect = SQLAlchemyError("Test error")

            with pytest.raises(SQLAlchemyError, match="Test error"):
                await update_user(
                    bio=new_bio,
                    avatar_name=new_avatar_name,
                    user=mock_user,
                    session=mock_db_session,
                )

            mock_db_session.commit.assert_awaited_once()
            mock_db_session.rollback.assert_awaited_once()
            mock_db_session.refresh.assert_not_awaited()


class TestEmail:
    class TestSendPlainMessage:
        def test_success(
            self,
            mock_background_tasks: Mock,
            mock_fastmail: MagicMock,
        ):
            subject = "Test subject"
            email_address = "test@example.com"
            body = "Test message"

            send_plain_message_to_email(
                subject=subject,
                email_address=email_address,
                body=body,
                background_tasks=mock_background_tasks,
            )

            mock_background_tasks.add_task.assert_called_once()
            args = mock_background_tasks.add_task.call_args[0]
            assert args[0] == mock_fastmail.send_message
            message = args[1]
            assert isinstance(message, MessageSchema)
            assert message.subject == subject
            assert message.recipients[0].email == email_address
            assert message.body == body
            assert message.subtype == MessageType.plain
            assert args[2] is None


@pytest.mark.anyio
class TestFiles:
    class TestSaveAvatar:
        async def test_success(self):
            mock_avatar = MagicMock(spec=UploadFile)
            mock_avatar.filename = "test.png"
            mock_avatar.read.return_value = b"test data"
            username = "username"
            avatar_name = "username.png"
            mock_file = AsyncMock()
            mock_file.__aenter__.return_value = mock_file
            mock_file.__aexit__.return_value = None
            with patch("aiofiles.open", return_value=mock_file) as mock_aiofiles_open:
                with patch("aiofiles.os.path.exists", new_callable=AsyncMock, return_value=False) as mock_exists:  # fmt: skip

                    result = await save_avatar(mock_avatar, username)

                    assert result == avatar_name
                    mock_avatar.read.assert_awaited_once()
                    mock_file.write.assert_awaited_once_with(b"test data")
                    mock_exists.assert_not_awaited()
                    mock_aiofiles_open.assert_called_once()

        async def test_with_exception_and_delete(self):
            mock_avatar = MagicMock(spec=UploadFile)
            mock_avatar.filename = "test.png"
            mock_avatar.read.side_effect = OSError("Test error")
            username = "username"
            mock_file = AsyncMock()
            mock_file.__aenter__.return_value = mock_file
            mock_file.__aexit__.return_value = None
            with patch("aiofiles.open", return_value=mock_file):
                with patch("aiofiles.os.path.exists", new_callable=AsyncMock, return_value=True) as mock_exists:  # fmt: skip
                    with patch("api.api_v1.utils.files.delete_avatar", new_callable=AsyncMock) as mock_delete:  # fmt: skip

                        with pytest.raises(OSError, match="Test error"):
                            await save_avatar(mock_avatar, username)

                        mock_exists.assert_called_once()
                        mock_delete.assert_called_once_with("username.png")

        async def test_with_exception_no_delete(self):
            mock_avatar = MagicMock(spec=UploadFile)
            mock_avatar.filename = "test.png"
            mock_avatar.read.side_effect = OSError("Test error")
            username = "username"
            mock_file = AsyncMock()
            mock_file.__aenter__.return_value = mock_file
            mock_file.__aexit__.return_value = None
            with patch("aiofiles.open", return_value=mock_file):
                with patch("aiofiles.os.path.exists", new_callable=AsyncMock, return_value=False) as mock_exists:  # fmt: skip
                    with patch("api.api_v1.utils.files.delete_avatar", new_callable=AsyncMock) as mock_delete:  # fmt: skip

                        with pytest.raises(OSError, match="Test error"):
                            await save_avatar(mock_avatar, username)

                        mock_exists.assert_called_once()
                        mock_delete.assert_not_called()

    class TestDeleteAvatar:
        async def test_success(self):
            avatar_name = "test.png"
            with patch("aiofiles.os.path.exists", new_callable=AsyncMock, return_value=True) as mock_exists:  # fmt: skip
                with patch("aiofiles.os.remove", new_callable=AsyncMock) as mock_remove:  # fmt: skip

                    await delete_avatar(avatar_name=avatar_name)

                    expected_path = settings.avatar.avatars_dir / avatar_name
                    mock_exists.assert_awaited_once_with(expected_path)
                    mock_remove.assert_awaited_once_with(expected_path)

        async def test_file_not_found(self):
            avatar_name = "nonexistent.png"
            with patch("aiofiles.os.path.exists", new_callable=AsyncMock, return_value=False) as mock_exists:  # fmt: skip
                with patch("aiofiles.os.remove", new_callable=AsyncMock) as mock_remove:  # fmt: skip

                    await delete_avatar(avatar_name=avatar_name)

                    expected_path = settings.avatar.avatars_dir / avatar_name
                    mock_exists.assert_awaited_once_with(expected_path)
                    mock_remove.assert_not_awaited()

        async def test_with_exception_no_delete(self):
            avatar_name = "test.png"
            with patch("aiofiles.os.path.exists", new_callable=AsyncMock, return_value=True) as mock_exists:  # fmt: skip
                with patch("aiofiles.os.remove", new_callable=AsyncMock, side_effect=OSError("Test error")) as mock_remove:  # fmt: skip

                    with pytest.raises(OSError, match="Test error"):
                        await delete_avatar(avatar_name)

                    expected_path = settings.avatar.avatars_dir / avatar_name
                    mock_exists.assert_awaited_once_with(expected_path)
                    mock_remove.assert_awaited_once_with(expected_path)


class TestJWTAuth:
    class TestEncodeJWT:
        def test_success(self, mock_datetime_now):
            payload = {"sub": 123}
            private_key = "test_private_key"
            algorithm = "RS256"
            expire_minutes = 30

            expected_result = "encoded_token"
            expected_exp = mock_datetime_now + datetime.timedelta(minutes=expire_minutes)  # fmt: skip
            expected_payload: dict[str, Any] = payload.copy()
            expected_jti = str(uuid.uuid4())
            expected_payload.update(
                jti=expected_jti,
                exp=expected_exp,
                iat=mock_datetime_now,
            )

            with patch("jwt.encode", return_value=expected_result) as mock_jwt_encode:
                with patch("uuid.uuid4", return_value=expected_jti):
                    result = encode_jwt(
                        payload=payload,
                        private_key=private_key,
                        algorithm=algorithm,
                        expire_minutes=expire_minutes,
                    )

                    mock_jwt_encode.assert_called_once_with(
                        payload=expected_payload,
                        key=private_key,
                        algorithm=algorithm,
                    )
                    assert result == expected_result

        def test_expire_minutes_zero(self, mock_datetime_now):
            payload = {"sub": 123}
            expected_jti = str(uuid.uuid4())
            expected_payload: dict[str, Any] = payload.copy()
            expected_payload.update(
                jti=expected_jti,
                exp=mock_datetime_now,
                iat=mock_datetime_now,
            )

            with patch("jwt.encode") as mock_jwt_encode:
                with patch("uuid.uuid4", return_value=expected_jti):
                    encode_jwt(payload=payload, expire_minutes=0)

                    kwargs = mock_jwt_encode.call_args[1]
                    assert kwargs["payload"] == expected_payload

        def test_with_exception(self, mock_datetime_now):
            payload = {"sub": 123}
            expected_payload: dict[str, Any] = payload.copy()
            expected_expire_minutes = mock_datetime_now + datetime.timedelta(
                minutes=settings.jwt_auth.access_token_expire_minutes
            )
            expected_jti = str(uuid.uuid4())
            expected_payload.update(
                jti=expected_jti,
                exp=expected_expire_minutes,
                iat=mock_datetime_now,
            )

            with patch('jwt.encode', side_effect=jwt.PyJWTError('Test error')) as mock_jwt_encode:  # fmt: skip
                with patch("uuid.uuid4", return_value=expected_jti):
                    with pytest.raises(jwt.PyJWTError, match="Test error"):
                        encode_jwt(payload=payload)

            mock_jwt_encode.assert_called_once_with(
                payload=expected_payload,
                key=settings.jwt_auth.private_key_path.read_text(),
                algorithm=settings.jwt_auth.algorithm,
            )

    class TestDecodeJWT:
        def test_success(self):
            token = "valid token"
            public_key = "test_public_key"
            algorithm = "RS256"
            expected_result = {"sub": 123}

            with patch("jwt.decode", return_value=expected_result) as mock_jwt_decode:
                result = decode_jwt(
                    token=token,
                    public_key=public_key,
                    algorithm=algorithm,
                )

                mock_jwt_decode.assert_called_once_with(
                    jwt=token,
                    key=public_key,
                    algorithms=[algorithm],
                )
                assert result == expected_result

        def test_invalid_token(self):
            token = "invalid token"
            public_key = "test_public_key"
            algorithm = "RS256"

            with patch("jwt.decode", side_effect=jwt.InvalidTokenError('Test error')) as mock_jwt_decode:  # fmt: skip
                with pytest.raises(jwt.InvalidTokenError, match="Test error"):
                    decode_jwt(
                        token=token,
                        public_key=public_key,
                        algorithm=algorithm,
                    )

                mock_jwt_decode.assert_called_once_with(
                    jwt=token,
                    key=public_key,
                    algorithms=[algorithm],
                )

        def test_expired_token(self):
            token = "expired token"
            public_key = "test_public_key"
            algorithm = "RS256"

            with patch("jwt.decode", side_effect=jwt.ExpiredSignatureError('Test error')) as mock_jwt_decode:  # fmt: skip
                with pytest.raises(jwt.ExpiredSignatureError, match="Test error"):
                    decode_jwt(
                        token=token,
                        public_key=public_key,
                        algorithm=algorithm,
                    )

                mock_jwt_decode.assert_called_once_with(
                    jwt=token,
                    key=public_key,
                    algorithms=[algorithm],
                )

    class TestCreateJWT:
        def test_success(self):
            token_type = "access"
            token_data: dict[str, Any] = {"sub": 123}
            expire_minutes = 30
            expected_payload = token_data.copy()
            expected_payload.update(
                {
                    settings.jwt_auth.token_type_payload_key: token_type,
                }
            )
            expected_result = "encoded_token"

            with patch("api.api_v1.utils.jwt_auth.encode_jwt", return_value=expected_result) as mock_encode_jwt:  # fmt: skip
                result = create_jwt(
                    token_type=token_type,
                    token_data=token_data,
                    expire_minutes=expire_minutes,
                )

                mock_encode_jwt.assert_called_once_with(
                    payload=expected_payload,
                    expire_minutes=expire_minutes,
                )
                assert result == expected_result

        def test_with_exception(self):
            token_type = "access"
            token_data: dict[str, Any] = {"sub": 123}
            expire_minutes = 30
            expected_payload = token_data.copy()
            expected_payload.update(
                {
                    settings.jwt_auth.token_type_payload_key: token_type,
                }
            )

            with patch("api.api_v1.utils.jwt_auth.encode_jwt", side_effect=jwt.PyJWTError('Test error')) as mock_encode_jwt:  # fmt: skip
                with pytest.raises(jwt.PyJWTError, match="Test error"):
                    create_jwt(
                        token_type=token_type,
                        token_data=token_data,
                        expire_minutes=expire_minutes,
                    )

                mock_encode_jwt.assert_called_once_with(
                    payload=expected_payload,
                    expire_minutes=expire_minutes,
                )

    class TestCreateAccessToken:
        def test_success(self):
            user = User(
                email="test@example.com",
                username="username",
            )
            expected_payload = {
                "sub": user.email,
                "username": user.username,
            }
            expected_result = "encoded_access_token"

            with patch("api.api_v1.utils.jwt_auth.create_jwt", return_value=expected_result) as mock_create_jwt:  # fmt: skip
                result = create_access_token(user=user)

                mock_create_jwt.assert_called_once_with(
                    token_type=settings.jwt_auth.access_token_type,
                    token_data=expected_payload,
                    expire_minutes=settings.jwt_auth.access_token_expire_minutes,
                )
                assert result == expected_result

        def test_with_exception(self):
            user = User(
                email="test@example.com",
                username="username",
            )
            expected_payload = {
                "sub": user.email,
                "username": user.username,
            }

            with patch("api.api_v1.utils.jwt_auth.create_jwt", side_effect=jwt.PyJWTError('Test error')) as mock_create_jwt:  # fmt: skip
                with pytest.raises(jwt.PyJWTError, match="Test error"):
                    create_access_token(user=user)

            mock_create_jwt.assert_called_once_with(
                token_type=settings.jwt_auth.access_token_type,
                token_data=expected_payload,
                expire_minutes=settings.jwt_auth.access_token_expire_minutes,
            )

    class TestCreateRefreshToken:
        def test_success(self):
            user = User(
                email="test@example.com",
            )
            expected_payload = {
                "sub": user.email,
            }
            expected_result = "encoded_refresh_token"

            with patch("api.api_v1.utils.jwt_auth.create_jwt", return_value=expected_result) as mock_create_jwt:  # fmt: skip
                result = create_refresh_token(user=user)

                mock_create_jwt.assert_called_once_with(
                    token_type=settings.jwt_auth.refresh_token_type,
                    token_data=expected_payload,
                    expire_minutes=settings.jwt_auth.refresh_token_expire_minutes,
                )
                assert result == expected_result

        def test_with_exception(self):
            user = User(
                email="test@example.com",
            )
            expected_payload = {
                "sub": user.email,
            }

            with patch("api.api_v1.utils.jwt_auth.create_jwt", side_effect=jwt.PyJWTError('Test error')) as mock_create_jwt:  # fmt: skip
                with pytest.raises(jwt.PyJWTError, match="Test error"):
                    create_refresh_token(user=user)

            mock_create_jwt.assert_called_once_with(
                token_type=settings.jwt_auth.refresh_token_type,
                token_data=expected_payload,
                expire_minutes=settings.jwt_auth.refresh_token_expire_minutes,
            )


class TestSecurity:
    class TestHashPassword:
        def test_success(self):
            password = "password"

            hashed_password = hash_password(password=password)

            assert hashed_password != password.encode()
            assert bcrypt.checkpw(password.encode(), hashed_password)

        def test_different_salts(self):
            password = "password"

            hashed_password1 = hash_password(password=password)
            hashed_password2 = hash_password(password=password)

            assert hashed_password1 != hashed_password2

    class TestVerifyPassword:
        def test_success(self):
            password = "password"
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

            assert verify_password(password=password, correct_password=hashed_password)

        def test_mismatched_passwords(self):
            password = "password"
            wrong_password = "wrongpassword"
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

            assert not verify_password(
                password=wrong_password,
                correct_password=hashed_password,
            )

    class TestValidateTokenType:
        def test_success(self):
            expected_type = "access"
            token_payload = {settings.jwt_auth.token_type_payload_key: expected_type}

            assert validate_token_type(
                token_payload=token_payload,
                expected_type=expected_type,
            )

        def test_failure(self):
            token_payload = {settings.jwt_auth.token_type_payload_key: "access"}
            expected_type = "refresh"

            assert not validate_token_type(
                token_payload=token_payload,
                expected_type=expected_type,
            )

    class TestGenerateEmailToken:
        def test_default_length(self):
            token = generate_email_token()

            assert len(token) == settings.email_tokens.token_length
            assert all(char in settings.email_tokens.token_symbols for char in token)

        def test_custom_length(self):
            length = 10
            token = generate_email_token(length=length)

            assert len(token) == length
            assert all(char in settings.email_tokens.token_symbols for char in token)

        def test_uniqueness(self):
            token1 = generate_email_token()
            token2 = generate_email_token()

            assert token1 != token2

    class TestValidateAvatarExtension:
        def test_success(self):
            avatar = MagicMock(spec=UploadFile, filename="avatar.jpg")

            assert validate_avatar_extension(avatar)

        def test_case_insensitive(self):
            avatar = MagicMock(spec=UploadFile, filename="avatar.JPG")

            assert validate_avatar_extension(avatar)

        def test_failure(self):
            avatar = MagicMock(spec=UploadFile, filename="avatar.txt")

            assert not validate_avatar_extension(avatar)

        def test_empty_filename(self):
            avatar = MagicMock(spec=UploadFile, filename="")

            assert not validate_avatar_extension(avatar)

        def test_no_extension(self):
            avatar = MagicMock(spec=UploadFile, filename="avatar")

            assert not validate_avatar_extension(avatar)

    @pytest.mark.anyio
    class TestValidateAvatarSize:
        async def test_success(self):
            image = Image.new("RGB", settings.avatar.size)
            image_bytes = BytesIO()
            image.save(image_bytes, format="JPEG")
            image_data = image_bytes.getvalue()
            avatar = MagicMock(spec=UploadFile)
            avatar.read = AsyncMock(return_value=image_data)
            avatar.seek = AsyncMock()

            assert await validate_avatar_size(avatar=avatar)

        async def test_failure(self):
            image = Image.new("RGB", (123, 456))
            image_bytes = BytesIO()
            image.save(image_bytes, format="JPEG")
            image_data = image_bytes.getvalue()
            avatar = MagicMock(spec=UploadFile)
            avatar.read = AsyncMock(return_value=image_data)
            avatar.seek = AsyncMock()

            assert not await validate_avatar_size(avatar=avatar)
