import re
import uuid

import jwt
import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.utils.database import (
    create_user,
    create_user_tokens,
    update_user_email_verification_token,
    update_forgot_password_token,
    get_user_by_username_or_email,
    get_user_by_email_verification_token,
    get_user_by_forgot_password_token,
    change_user_password,
    confirm_user_email,
    create_story,
    get_stories,
    get_story_by_uuid,
    get_author_stories,
    edit_story,
    like_story,
    delete_story,
)
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
)
from core.config import settings
from core.models import User, Token


class TestSecurity:
    def test_hash_password(self):
        hashed_password = hash_password(password="password")
        assert isinstance(hashed_password, bytes)

    def test_verify_password(self):
        hashed_password = hash_password(password="password")
        assert verify_password(
            password="password",
            correct_password=hashed_password,
        )

    def test_verify_incorrect_password(self):
        hashed_password = hash_password(password="password")
        assert not verify_password(
            password="secret",
            correct_password=hashed_password,
        )

    def test_verify_token_type(
        self,
        token_data: dict,
    ):
        assert validate_token_type(
            token_payload=token_data,
            expected_type=token_data[settings.jwt_auth.token_type_payload_key],
        )

    def test_verify_invalid_token_type(
        self,
        token_data: dict,
    ):
        assert not validate_token_type(
            token_payload=token_data,
            expected_type="other_token_type",
        )

    def test_generate_email_token(self):
        email_token = generate_email_token()
        assert re.match(pattern=r"[a-z0-9]{6}", string=email_token)

    def test_generate_email_token_with_arg(self):
        email_token = generate_email_token(length=12)
        assert re.match(pattern=r"[a-z0-9]{12}", string=email_token)


class TestJwt:
    def test_encode_jwt(
        self,
        token_data: dict,
    ):
        encoded = encode_jwt(payload=token_data)
        assert isinstance(encoded, str)

    def test_encode_jwt_empty_payload(self):
        encoded = encode_jwt(payload={})
        assert isinstance(encoded, str)

    def test_encode_jwt_invalid_private_key(
        self,
        token_data: dict,
    ):
        with pytest.raises(jwt.exceptions.InvalidKeyError):
            encode_jwt(
                payload=token_data,
                private_key="invalid_key",
            )

    def test_decode_jwt(
        self,
        token_data: dict,
    ):
        encoded = encode_jwt(payload=token_data)
        decoded = decode_jwt(token=encoded)
        assert decoded["sub"] == token_data["sub"]
        assert decoded["username"] == token_data["username"]
        assert (
            decoded[settings.jwt_auth.token_type_payload_key]
            == token_data[settings.jwt_auth.token_type_payload_key]
        )

    def test_decode_jwt_invalid_token(self):
        invalid_token = "invalid_jwt_token"
        with pytest.raises(jwt.exceptions.DecodeError):
            decode_jwt(token=invalid_token)

    def test_decode_jwt_expired_token(
        self,
        token_data: dict,
    ):
        encoded = encode_jwt(
            payload=token_data,
            expire_minutes=-1,
        )
        with pytest.raises(jwt.ExpiredSignatureError):
            decode_jwt(token=encoded)

    def test_decode_jwt_invalid_algorithm(
        self,
        token_data: dict,
    ):
        encoded = encode_jwt(payload=token_data)
        with pytest.raises(jwt.InvalidAlgorithmError):
            decode_jwt(token=encoded, algorithm="HS256")

    def test_decode_jwt_invalid_public_key(
        self,
        token_data: dict,
    ):
        encoded = encode_jwt(payload=token_data)
        with pytest.raises(jwt.exceptions.InvalidKeyError):
            decode_jwt(token=encoded, public_key="invalid_public_key")

    def test_create_jwt(
        self,
        token_data: dict,
    ):
        expire_minutes = 15
        token = create_jwt(
            token_type=token_data[settings.jwt_auth.token_type_payload_key],
            token_data=token_data,
            expire_minutes=expire_minutes,
        )
        decoded = decode_jwt(token=token)
        assert decoded["sub"] == token_data["sub"]
        assert decoded["username"] == token_data["username"]
        assert (
            decoded[settings.jwt_auth.token_type_payload_key]
            == token_data[settings.jwt_auth.token_type_payload_key]
        )

    def test_create_jwt_empty_token_data(self):
        token_data = {}
        token_type = ""
        expire_minutes = 15
        token = create_jwt(
            token_type=token_type,
            token_data=token_data,
            expire_minutes=expire_minutes,
        )
        decoded = decode_jwt(token=token)
        assert decoded[settings.jwt_auth.token_type_payload_key] == token_type

    def test_create_access_token(
        self,
        first_user: User,
    ):
        access_token = create_access_token(user=first_user)
        decoded = decode_jwt(token=access_token)
        assert decoded["sub"] == first_user.email
        assert decoded["username"] == first_user.username
        assert (
            decoded[settings.jwt_auth.token_type_payload_key]
            == settings.jwt_auth.access_token_type
        )

    def test_create_refresh_token(
        self,
        first_user: User,
    ):
        access_token = create_refresh_token(user=first_user)
        decoded = decode_jwt(token=access_token)
        assert decoded["sub"] == first_user.email
        assert (
            decoded[settings.jwt_auth.token_type_payload_key]
            == settings.jwt_auth.refresh_token_type
        )


@pytest.mark.anyio
class TestDatabase:
    async def test_create_user(
        self,
        session: AsyncSession,
        first_user: User,
    ):
        hashed_password = hash_password("password")
        new_user = await create_user(
            username=first_user.username,
            email=first_user.email,
            hashed_password=hashed_password,
            session=session,
        )
        assert new_user.username == first_user.username
        assert new_user.email == first_user.email
        assert new_user.hashed_password == hashed_password

    async def test_create_user2(
        self,
        session: AsyncSession,
        second_user: User,
    ):
        hashed_password = hash_password("password")
        new_user = await create_user(
            username=second_user.username,
            email=second_user.email,
            hashed_password=hashed_password,
            session=session,
        )
        assert new_user.username == second_user.username
        assert new_user.email == second_user.email
        assert new_user.hashed_password == hashed_password

    async def test_create_user_same_username(
        self,
        first_user: User,
        session: AsyncSession,
    ):
        with pytest.raises(IntegrityError):
            await create_user(
                username=first_user.username,
                email="other_email@email.com",
                hashed_password=first_user.hashed_password,
                session=session,
            )

    async def test_create_user_same_email(
        self,
        first_user: User,
        session: AsyncSession,
    ):
        with pytest.raises(IntegrityError):
            await create_user(
                username="other_username",
                email=first_user.email,
                hashed_password=first_user.hashed_password,
                session=session,
            )

    async def test_create_user_tokens(
        self,
        first_user: User,
        session: AsyncSession,
    ):
        tokens = await create_user_tokens(email=first_user.email, session=session)
        assert tokens.email == first_user.email

    async def test_create_user_tokens_existing_email(
        self,
        second_user: User,
        session: AsyncSession,
    ):
        await create_user_tokens(email=second_user.email, session=session)
        with pytest.raises(IntegrityError):
            await create_user_tokens(email=second_user.email, session=session)

    async def test_create_user_tokens_nonexistent_email(
        self,
        session: AsyncSession,
    ):
        with pytest.raises(IntegrityError):
            await create_user_tokens(email="nonexistent_email", session=session)

    async def test_update_user_email_verification_token(
        self,
        first_user: User,
        session: AsyncSession,
    ):
        stmt = select(Token).where(Token.email == first_user.email)
        user_tokens = await session.execute(stmt)
        user_tokens = user_tokens.scalar_one()
        tokens = await update_user_email_verification_token(
            user_tokens=user_tokens,
            email_verification_token=first_user.tokens.email_verification_token,
            session=session,
        )
        assert tokens.email == first_user.email
        assert (
            tokens.email_verification_token
            == first_user.tokens.email_verification_token
        )

    async def test_update_forgot_password_token(
        self,
        first_user: User,
        session: AsyncSession,
    ):
        stmt = select(Token).where(Token.email == first_user.email)
        user_tokens = await session.execute(stmt)
        user_tokens = user_tokens.scalar_one()
        tokens = await update_forgot_password_token(
            user_tokens=user_tokens,
            forgot_password_token=first_user.tokens.forgot_password_token,
            session=session,
        )
        assert tokens.email == first_user.email
        assert tokens.forgot_password_token == first_user.tokens.forgot_password_token

    async def test_get_user_by_username(
        self,
        first_user: User,
        session: AsyncSession,
    ):
        user = await get_user_by_username_or_email(
            username=first_user.username,
            session=session,
        )
        assert user.email == first_user.email
        assert user.username == first_user.username

    async def test_get_user_by_email(
        self,
        first_user: User,
        session: AsyncSession,
    ):
        user = await get_user_by_username_or_email(
            email=first_user.email,
            session=session,
        )
        assert user.email == first_user.email
        assert user.username == first_user.username

    async def test_get_user_by_invalid_username(
        self,
        first_user: User,
        session: AsyncSession,
    ):
        user = await get_user_by_username_or_email(
            username="invalid_username",
            session=session,
        )
        assert user is None

    async def test_get_user_by_invalid_email(
        self,
        first_user: User,
        session: AsyncSession,
    ):
        user = await get_user_by_username_or_email(
            email="invalid_email",
            session=session,
        )
        assert user is None

    async def test_get_user_by_email_verification_token(
        self,
        first_user: User,
        session: AsyncSession,
    ):
        user = await get_user_by_email_verification_token(
            email_verification_token=first_user.tokens.email_verification_token,
            session=session,
        )
        assert user.email == first_user.email
        assert user.username == first_user.username

    async def test_get_user_by_forgot_password_token(
        self,
        first_user: User,
        session: AsyncSession,
    ):
        user = await get_user_by_forgot_password_token(
            forgot_password_token=first_user.tokens.forgot_password_token,
            session=session,
        )
        assert user.email == first_user.email
        assert user.username == first_user.username

    async def test_get_user_by_invalid_email_verification_token(
        self,
        first_user: User,
        session: AsyncSession,
    ):
        user = await get_user_by_email_verification_token(
            email_verification_token="invalid_token",
            session=session,
        )
        assert user is None

    async def test_get_user_by_invalid_forgot_password_token(
        self,
        first_user: User,
        session: AsyncSession,
    ):
        user = await get_user_by_forgot_password_token(
            forgot_password_token="invalid_token",
            session=session,
        )
        assert user is None

    async def test_change_password(
        self,
        first_user: User,
        session: AsyncSession,
    ):
        first_user = await get_user_by_username_or_email(
            username=first_user.username,
            session=session,
        )
        new_hashed_password = hash_password(password="new_password")
        user = await change_user_password(
            user=first_user,
            new_hashed_password=new_hashed_password,
            session=session,
        )
        assert user.hashed_password == new_hashed_password

    async def test_confirm_user_email(
        self,
        first_user: User,
        session: AsyncSession,
    ):
        first_user = await get_user_by_username_or_email(
            username=first_user.username,
            session=session,
        )
        assert not first_user.is_email_verified
        await confirm_user_email(user=first_user, session=session)
        assert first_user.is_email_verified

    async def test_create_story_nonexistent_author(
        self,
        session: AsyncSession,
    ):
        with pytest.raises(IntegrityError):
            await create_story(
                name="test story name",
                text="test story text",
                author_email="nonexistent@email.com",
                session=session,
            )

    @pytest.mark.parametrize(
        "name,text",
        (
            ("first test story name", "first test story text"),
            ("second test story name", "second test story text"),
        ),
    )
    async def test_create_story_success(
        self,
        first_user: User,
        session: AsyncSession,
        name: str,
        text: str,
    ):
        story = await create_story(
            name=name,
            text=text,
            author_email=first_user.email,
            session=session,
        )
        assert story.name == name
        assert story.text == text
        assert story.author_email == first_user.email

    async def test_get_stories(
        self,
        session: AsyncSession,
    ):
        stories = await get_stories(session=session)
        assert len(stories) == 2

    async def test_get_story_by_invalid_uuid(
        self,
        session: AsyncSession,
    ):
        story = await get_story_by_uuid(
            story_uuid=uuid.uuid4(),
            session=session,
        )
        assert story is None

    async def test_get_story_by_uuid(
        self,
        session: AsyncSession,
    ):
        stories = await get_stories(session=session)
        story = await get_story_by_uuid(
            story_uuid=stories[0].id,
            session=session,
        )
        assert story is not None

    async def test_get_author_stories_nonexistent(
        self,
        session: AsyncSession,
    ):
        stories = await get_author_stories(
            author_username="nonexistent",
            session=session,
        )
        assert len(stories) == 0

    async def test_get_author_stories(
        self,
        session: AsyncSession,
        first_user: User,
    ):
        stories = await get_author_stories(
            author_username=first_user.username,
            session=session,
        )
        assert len(stories) == 2

    async def test_edit_story(
        self,
        session: AsyncSession,
        first_user: User,
    ):
        stories = await get_author_stories(
            author_username=first_user.username,
            session=session,
        )
        story = stories[0]
        edited_story = await edit_story(
            name="edited test story name",
            text="edited test story text",
            story=story,
            session=session,
        )
        story_with_changes = await get_story_by_uuid(
            story_uuid=story.id,
            session=session,
        )
        assert edited_story.name == story_with_changes.name
        assert edited_story.text == story_with_changes.text

    async def test_like_story(
        self,
        session: AsyncSession,
        first_user: User,
    ):
        stories = await get_author_stories(
            author_username=first_user.username,
            session=session,
        )
        story = stories[0]
        await like_story(story=story, user=story.author, session=session)
        liked_story = await get_story_by_uuid(
            story_uuid=story.id,
            session=session,
        )
        assert liked_story.likes_number == 1

    async def test_delete_story(
        self,
        session: AsyncSession,
        first_user: User,
    ):
        stories = await get_author_stories(
            author_username=first_user.username,
            session=session,
        )
        story = stories[0]
        await delete_story(story=story, session=session)
        deleted_story = await get_story_by_uuid(
            story_uuid=story.id,
            session=session,
        )
        assert deleted_story is None
