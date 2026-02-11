import datetime
import functools
import inspect
from typing import Callable, Sequence
from uuid import UUID

from pydantic import EmailStr
from sqlalchemy import select, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from core.config import settings
from core.models import User, Token, Story
from core.models.user import Role


def _rollback_if_db_exception(session_param_name: str = "session"):
    def inner(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            session = kwargs.get(session_param_name)

            # пользователь может передать сессию позиционным аргументом,
            # поэтому нам нужно проверить еще и args
            if session is None:
                signature = inspect.signature(func)
                param_names = list(signature.parameters.keys())
                try:
                    session_index = param_names.index(session_param_name)
                    session = args[session_index]
                except ValueError, IndexError:
                    pass

            if session is None:
                raise ValueError(
                    f"Function {func.__name__} has no '{session_param_name}' parameter"
                )
            if not isinstance(session, AsyncSession):
                raise ValueError("Session object does not have rollback method")

            try:
                result = await func(*args, **kwargs)
                return result
            except SQLAlchemyError:
                await session.rollback()
                raise

        return wrapper

    return inner


async def get_user_by_username_or_email(
    session: AsyncSession,
    username: str = "",
    email: str | EmailStr = "",
    load_tokens: bool = False,
    load_stories: bool = False,
    load_liked_stories: bool = False,
) -> User | None:
    stmt = select(User).where(or_(User.username == username, User.email == email))
    if load_tokens:
        stmt = stmt.options(joinedload(User.tokens))
    if load_stories:
        stmt = stmt.options(selectinload(User.stories))
    if load_liked_stories:
        stmt = stmt.options(selectinload(User.liked_stories))
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    return user


async def get_user_by_email_verification_token(
    email_verification_token: str,
    session: AsyncSession,
    load_tokens: bool = False,
    load_stories: bool = False,
    load_liked_stories: bool = False,
) -> User | None:
    stmt = (
        select(User)
        .join(User.tokens)
        .where(Token.email_verification_token == email_verification_token)
    )
    if load_tokens:
        stmt = stmt.options(joinedload(User.tokens))
    if load_stories:
        stmt = stmt.options(selectinload(User.stories))
    if load_liked_stories:
        stmt = stmt.options(selectinload(User.liked_stories))
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    return user


async def get_user_by_forgot_password_token(
    forgot_password_token: str,
    session: AsyncSession,
    load_tokens: bool = False,
    load_stories: bool = False,
    load_liked_stories: bool = False,
) -> User | None:
    stmt = (
        select(User)
        .join(User.tokens)
        .where(Token.forgot_password_token == forgot_password_token)
    )
    if load_tokens:
        stmt = stmt.options(joinedload(User.tokens))
    if load_stories:
        stmt = stmt.options(selectinload(User.stories))
    if load_liked_stories:
        stmt = stmt.options(selectinload(User.liked_stories))
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    return user


@_rollback_if_db_exception()
async def create_user_with_tokens(
    username: str,
    hashed_password: bytes,
    email: str | EmailStr,
    session: AsyncSession,
) -> None:
    new_user = User(
        email=email,
        username=username,
        hashed_password=hashed_password,
    )
    tokens = Token(username=username)
    session.add(new_user)
    session.add(tokens)
    await session.commit()


@_rollback_if_db_exception()
async def update_user_email_verification_token(
    user: User,
    email_verification_token: str,
    session: AsyncSession,
    expire_minutes: int = settings.email_tokens.email_verification_token_exp_minutes,
) -> User:
    email_verification_token_exp = datetime.datetime.now(
        datetime.UTC
    ) + datetime.timedelta(minutes=expire_minutes)
    user.tokens.email_verification_token = email_verification_token
    user.tokens.email_verification_token_exp = email_verification_token_exp
    await session.commit()
    await session.refresh(user)
    return user


@_rollback_if_db_exception()
async def confirm_user_email(
    user: User,
    session: AsyncSession,
) -> None:
    user.is_email_verified = True
    user.tokens.email_verification_token = None
    user.tokens.email_verification_token_exp = None
    await session.commit()


@_rollback_if_db_exception()
async def update_forgot_password_token(
    user: User,
    forgot_password_token: str,
    session: AsyncSession,
    expire_minutes: int = settings.email_tokens.forgot_password_token_exp_minutes,
) -> User:
    forgot_password_token_exp = datetime.datetime.now(
        datetime.UTC
    ) + datetime.timedelta(minutes=expire_minutes)
    user.tokens.forgot_password_token = forgot_password_token
    user.tokens.forgot_password_token_exp = forgot_password_token_exp
    await session.commit()
    await session.refresh(user)
    return user


@_rollback_if_db_exception()
async def change_user_password(
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


async def get_stories(
    session: AsyncSession,
    load_author: bool = False,
    load_likers: bool = False,
    page: int = 1,
    per_page: int = 20,
) -> Sequence[Story]:
    offset = (page - 1) * per_page
    stmt = select(Story)
    if load_author:
        stmt = stmt.options(joinedload(Story.author))
    if load_likers:
        stmt = stmt.options(selectinload(Story.likers))
    result = await session.execute(
        stmt.order_by(Story.created_at.desc()).offset(offset).limit(per_page)
    )
    stories = result.scalars().fetchall()
    return stories


async def get_stories_by_name_or_text(
    query: str,
    session: AsyncSession,
    load_author: bool = False,
    load_likers: bool = False,
    page: int = 1,
    per_page: int = 20,
) -> Sequence[Story]:
    offset = (page - 1) * per_page
    stmt = select(Story)
    if load_author:
        stmt = stmt.options(joinedload(Story.author))
    if load_likers:
        stmt = stmt.options(selectinload(Story.likers))
    result = await session.execute(
        stmt.where(or_(Story.name.ilike(f"%{query}%"), Story.text.ilike(f"%{query}%")))
        .order_by(Story.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    stories = result.scalars().fetchall()
    return stories


async def get_story_by_uuid(
    story_uuid: UUID,
    session: AsyncSession,
    load_author: bool = False,
    load_likers: bool = False,
) -> Story | None:
    stmt = select(Story)
    if load_author:
        stmt = stmt.options(joinedload(Story.author))
    if load_likers:
        stmt = stmt.options(selectinload(Story.likers))
    result = await session.execute(stmt.where(Story.id == story_uuid))
    story = result.scalar_one_or_none()
    return story


@_rollback_if_db_exception()
async def create_story(
    name: str,
    text: str,
    author_username: str,
    session: AsyncSession,
) -> Story:
    new_story = Story(
        name=name,
        text=text,
        author_username=author_username,
    )
    session.add(new_story)
    await session.commit()
    await session.refresh(new_story)
    return new_story


@_rollback_if_db_exception()
async def edit_story(
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


@_rollback_if_db_exception()
async def delete_story(
    story: Story,
    session: AsyncSession,
) -> None:
    await session.delete(story)
    await session.commit()


@_rollback_if_db_exception()
async def like_story(
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


@_rollback_if_db_exception()
async def update_user(
    user: User,
    session: AsyncSession,
    bio: str | None = None,
    avatar_name: str | None = None,
) -> User:
    user.bio = bio
    user.avatar_name = avatar_name
    await session.commit()
    await session.refresh(user)
    return user


async def get_active_users(
    session: AsyncSession,
    load_tokens: bool = False,
    load_stories: bool = False,
    load_liked_stories: bool = False,
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
    if load_tokens:
        stmt = stmt.options(joinedload(User.tokens))
    if load_stories:
        stmt = stmt.options(selectinload(User.stories))
    if load_liked_stories:
        stmt = stmt.options(selectinload(User.liked_stories))
    result = await session.execute(stmt)
    users = result.scalars().fetchall()
    return users


async def get_inactive_users(
    session: AsyncSession,
    load_tokens: bool = False,
    load_stories: bool = False,
    load_liked_stories: bool = False,
    page: int = 1,
    per_page: int = 20,
) -> Sequence[User]:
    offset = (page - 1) * per_page
    stmt = (
        select(User)
        .where(~User.is_active)
        .order_by(User.registered_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    if load_tokens:
        stmt = stmt.options(joinedload(User.tokens))
    if load_stories:
        stmt = stmt.options(selectinload(User.stories))
    if load_liked_stories:
        stmt = stmt.options(selectinload(User.liked_stories))
    result = await session.execute(stmt)
    users = result.scalars().fetchall()
    return users


@_rollback_if_db_exception()
async def make_admin(
    user: User,
    session: AsyncSession,
) -> User:
    user.role = Role.ADMIN
    await session.commit()
    await session.refresh(user)
    return user


@_rollback_if_db_exception()
async def demote_admin(
    user: User,
    session: AsyncSession,
) -> User:
    user.role = Role.USER
    await session.commit()
    await session.refresh(user)
    return user


@_rollback_if_db_exception()
async def block_user(
    user: User,
    session: AsyncSession,
) -> User:
    user.is_active = False
    await session.commit()
    await session.refresh(user)
    return user


@_rollback_if_db_exception()
async def unblock_user(
    user: User,
    session: AsyncSession,
) -> User:
    user.is_active = True
    await session.commit()
    await session.refresh(user)
    return user
