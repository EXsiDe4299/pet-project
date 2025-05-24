import datetime
import functools
from typing import Sequence, Callable
from uuid import UUID

from sqlalchemy import select, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import User, Story
from core.models.token import Token
from core.models.user import Role


def __rollback_if_db_exception():
    def wrapper(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapped(**kwargs):
            session = None
            try:
                session = kwargs.get("session")
                result = await func(**kwargs)
                return result
            except SQLAlchemyError:
                await session.rollback()
                raise

        return wrapped

    return wrapper


async def get_user_by_username_or_email(
    session: AsyncSession,
    username: str = "",
    email: str = "",
) -> User | None:
    stmt = select(User).where(or_(User.username == username, User.email == email))
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    return user


async def get_user_by_email_verification_token(
    email_verification_token: str,
    session: AsyncSession,
) -> User | None:
    stmt = (
        select(User)
        .join(User.tokens)
        .where(Token.email_verification_token == email_verification_token)
    )
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    return user


async def get_user_by_forgot_password_token(
    forgot_password_token: str,
    session: AsyncSession,
) -> User | None:
    stmt = (
        select(User)
        .join(User.tokens)
        .where(Token.forgot_password_token == forgot_password_token)
    )
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    return user


@__rollback_if_db_exception()
async def create_user_with_tokens(
    *,
    username: str,
    hashed_password: bytes,
    email: str,
    session: AsyncSession,
) -> None:
    new_user = User(
        email=email,
        username=username,
        hashed_password=hashed_password,
    )
    tokens = Token(email=email)
    session.add(new_user)
    session.add(tokens)
    await session.commit()


@__rollback_if_db_exception()
async def update_user_email_verification_token(
    *,
    user_tokens: Token,
    email_verification_token: str,
    session: AsyncSession,
    expire_minutes: int = settings.email_tokens.email_verification_token_exp_minutes,
) -> Token:
    email_verification_token_exp = datetime.datetime.now(
        datetime.UTC
    ) + datetime.timedelta(minutes=expire_minutes)
    user_tokens.email_verification_token = email_verification_token
    user_tokens.email_verification_token_exp = email_verification_token_exp
    await session.commit()
    await session.refresh(user_tokens)
    return user_tokens


@__rollback_if_db_exception()
async def update_forgot_password_token(
    *,
    user_tokens: Token,
    forgot_password_token: str,
    session: AsyncSession,
    expire_minutes: int = settings.email_tokens.forgot_password_token_exp_minutes,
) -> Token:
    forgot_password_token_exp = datetime.datetime.now(
        datetime.UTC
    ) + datetime.timedelta(minutes=expire_minutes)
    user_tokens.forgot_password_token = forgot_password_token
    user_tokens.forgot_password_token_exp = forgot_password_token_exp
    await session.commit()
    await session.refresh(user_tokens)
    return user_tokens


@__rollback_if_db_exception()
async def change_user_password(
    *,
    user: User,
    new_hashed_password: bytes,
    session: AsyncSession,
) -> User:
    user.hashed_password = new_hashed_password
    user.tokens.forgot_password_token = None
    user.tokens.forgot_password_token_exp = None
    await session.commit()
    await session.refresh(user)
    return user


@__rollback_if_db_exception()
async def confirm_user_email(
    *,
    user: User,
    session: AsyncSession,
) -> None:
    user.is_email_verified = True
    user.tokens.email_verification_token = None
    user.tokens.email_verification_token_exp = None
    await session.commit()


async def get_stories(
    session: AsyncSession,
    page: int = 1,
    per_page: int = 20,
) -> Sequence[Story]:
    offset = (page - 1) * per_page
    result = await session.execute(
        select(Story, User)
        .join(User, User.email == Story.author_email)
        .order_by(Story.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    stories = result.unique().scalars().fetchall()
    return stories


async def get_stories_by_name_or_text(
    query: str,
    session: AsyncSession,
    page: int = 1,
    per_page: int = 20,
) -> Sequence[Story]:
    offset = (page - 1) * per_page
    result = await session.execute(
        select(Story, User)
        .join(User, User.email == Story.author_email)
        .where(or_(Story.name.ilike(f"%{query}%"), Story.text.ilike(f"%{query}%")))
        .order_by(Story.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    stories = result.unique().scalars().fetchall()
    return stories


async def get_story_by_uuid(
    story_uuid: UUID,
    session: AsyncSession,
) -> Story | None:
    result = await session.execute(
        select(Story, User)
        .join(User, User.email == Story.author_email)
        .where(Story.id == story_uuid)
    )
    story = result.unique().scalar_one_or_none()
    return story


async def get_author_stories(
    author_username: str,
    session: AsyncSession,
    page: int = 1,
    per_page: int = 20,
) -> Sequence[Story]:
    offset = (page - 1) * per_page
    result = await session.execute(
        select(Story, User)
        .join(User, User.email == Story.author_email)
        .where(User.username == author_username)
        .order_by(Story.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    stories = result.unique().scalars().fetchall()
    return stories


@__rollback_if_db_exception()
async def create_story(
    *,
    name: str,
    text: str,
    author_email: str,
    session: AsyncSession,
) -> Story:
    new_story = Story(
        name=name,
        text=text,
        author_email=author_email,
    )
    session.add(new_story)
    await session.commit()
    await session.refresh(new_story)
    return new_story


@__rollback_if_db_exception()
async def edit_story(
    *,
    name: str,
    text: str,
    story: Story,
    session: AsyncSession,
) -> Story:
    story.name = name
    story.text = text
    await session.commit()
    await session.refresh(story)
    return story


@__rollback_if_db_exception()
async def delete_story(
    *,
    story: Story,
    session: AsyncSession,
) -> None:
    await session.delete(story)
    await session.commit()


@__rollback_if_db_exception()
async def like_story(
    *,
    story: Story,
    user: User,
    session: AsyncSession,
) -> Story:
    if user not in story.likers:
        story.likes_number += 1
        story.likers.append(user)
    else:
        story.likes_number -= 1
        story.likers.remove(user)
    await session.commit()
    await session.refresh(story)
    return story


@__rollback_if_db_exception()
async def update_user(
    *,
    bio: str | None = None,
    avatar_name: str | None = None,
    user: User,
    session: AsyncSession,
) -> User:
    user.bio = bio
    user.avatar_name = avatar_name
    await session.commit()
    await session.refresh(user)
    return user


async def get_active_users(
    session: AsyncSession,
    page: int = 1,
    per_page: int = 20,
) -> Sequence[User]:
    offset = (page - 1) * per_page
    stmt = (
        select(User)
        .where(User.is_active)
        .order_by(User.registered_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    result = await session.execute(stmt)
    users = result.scalars().fetchall()
    return users


async def get_inactive_users(
    session: AsyncSession,
    page: int = 1,
    per_page: int = 20,
) -> Sequence[User]:
    offset = (page - 1) * per_page
    stmt = (
        select(User)
        .where(User.is_active == False)
        .order_by(User.registered_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    result = await session.execute(stmt)
    users = result.scalars().fetchall()
    return users


@__rollback_if_db_exception()
async def make_admin(
    user: User,
    session: AsyncSession,
) -> User:
    user.role = Role.ADMIN
    await session.commit()
    await session.refresh(user)
    return user


@__rollback_if_db_exception()
async def demote_admin(
    user: User,
    session: AsyncSession,
) -> User:
    user.role = Role.USER
    await session.commit()
    await session.refresh(user)
    return user


@__rollback_if_db_exception()
async def block_user(
    *,
    user: User,
    session: AsyncSession,
) -> User:
    user.is_active = False
    await session.commit()
    await session.refresh(user)
    return user


@__rollback_if_db_exception()
async def unblock_user(
    *,
    user: User,
    session: AsyncSession,
) -> User:
    user.is_active = True
    await session.commit()
    await session.refresh(user)
    return user
