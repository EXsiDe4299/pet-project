import datetime

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from core.config import settings
from core.models import User
from core.models.token import Token


async def get_user_by_username(
    username: str,
    session: AsyncSession,
) -> User | None:
    stmt = (
        select(User).options(joinedload(User.tokens)).where(User.username == username)
    )
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    return user


async def get_user_by_username_or_email(
    username: str,
    email: str,
    session: AsyncSession,
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
        username=username,
        hashed_password=hashed_password,
        email=email,
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


async def create_user_tokens(
    username: str,
    session: AsyncSession,
) -> Token:
    tokens = Token(username=username)
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


async def confirm_user_email(
    user: User,
    session: AsyncSession,
) -> None:
    user.is_email_verified = True
    user.tokens.email_verification_token = None
    user.tokens.email_verification_token_exp = None
    await session.commit()
