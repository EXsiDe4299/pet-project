import datetime
from typing import Sequence
from uuid import UUID

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from core.config import settings
from core.models import User, Story
from core.models.token import Token


async def get_user_by_username_or_email(
    session: AsyncSession,
    username: str = "",
    email: str = "",
) -> User | None:
    stmt = (
        select(User)
        .options(joinedload(User.tokens))
        .where(or_(User.username == username, User.email == email))
    )
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
        .options(joinedload(User.tokens))
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
        .options(joinedload(User.tokens))
    )
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    return user


async def create_user(
    username: str,
    hashed_password: bytes,
    email: str,
    session: AsyncSession,
) -> User:
    new_user = User(
        email=email,
        username=username,
        hashed_password=hashed_password,
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


async def create_user_tokens(
    email: str,
    session: AsyncSession,
) -> Token:
    tokens = Token(email=email)
    session.add(tokens)
    await session.commit()
    await session.refresh(tokens)
    return tokens


async def update_user_email_verification_token(
    user_tokens: Token,
    email_verification_token: str,
    session: AsyncSession,
    expire_minutes: int = settings.email_tokens.email_verification_token_exp_minutes,
) -> Token:
    email_verification_token_exp = datetime.datetime.now() + datetime.timedelta(
        minutes=expire_minutes
    )
    user_tokens.email_verification_token = email_verification_token
    user_tokens.email_verification_token_exp = email_verification_token_exp
    await session.commit()
    await session.refresh(user_tokens)
    return user_tokens


async def update_forgot_password_token(
    user_tokens: Token,
    forgot_password_token: str,
    session: AsyncSession,
    expire_minutes: int = settings.email_tokens.forgot_password_token_exp_minutes,
) -> Token:
    forgot_password_token_exp = datetime.datetime.now() + datetime.timedelta(
        minutes=expire_minutes
    )
    user_tokens.forgot_password_token = forgot_password_token
    user_tokens.forgot_password_token_exp = forgot_password_token_exp
    await session.commit()
    await session.refresh(user_tokens)
    return user_tokens


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


async def confirm_user_email(
    user: User,
    session: AsyncSession,
) -> None:
    user.is_email_verified = True
    user.tokens.email_verification_token = None
    user.tokens.email_verification_token_exp = None
    await session.commit()


async def get_stories(
    session: AsyncSession,
) -> Sequence[Story]:
    result = await session.execute(select(Story).options(selectinload(Story.author)))
    stories = result.scalars().fetchall()
    return stories


async def get_story_by_uuid(
    story_uuid: UUID,
    session: AsyncSession,
) -> Story:
    result = await session.execute(
        select(Story)
        .where(Story.id == story_uuid)
        .options(selectinload(Story.likers))
        .options(selectinload(Story.author))
    )
    story = result.scalar_one_or_none()
    return story


async def get_author_stories(
    author_username: str,
    session: AsyncSession,
) -> Sequence[Story]:
    result = await session.execute(
        select(Story)
        .where(User.username == author_username)
        .options(selectinload(Story.likers))
        .options(selectinload(Story.author))
    )
    stories = result.scalars().fetchall()
    return stories


async def create_story(
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


async def delete_story(
    story: Story,
    session: AsyncSession,
):
    await session.delete(story)
    await session.commit()


async def like_story(
    story: Story,
    user: User,
    session: AsyncSession,
):
    if user not in story.likers:
        story.likes_number += 1
        story.likers.append(user)
    else:
        story.likes_number -= 1
        story.likers.remove(user)
    await session.commit()
