from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User


async def get_user_by_username(
    username: str,
    session: AsyncSession,
) -> User | None:
    stmt = select(User).where(User.username == username)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    return user


async def create_user(
    username: str,
    hashed_password: bytes,
    email: str,
    email_verification_token: str,
    session: AsyncSession,
) -> User:
    new_user = User(
        username=username,
        hashed_password=hashed_password,
        email=email,
        email_verification_token=email_verification_token,
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user
