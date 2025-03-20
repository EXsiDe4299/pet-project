from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import expression

from core.models.base import Base

if TYPE_CHECKING:
    from core.models import Token, Story


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    hashed_password: Mapped[bytes] = mapped_column(nullable=False)
    bio: Mapped[str] = mapped_column(
        Text(),
        nullable=True,
    )
    avatar_name: Mapped[str] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(
        nullable=False,
        default=True,
        server_default=expression.true(),
    )
    is_email_verified: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
        server_default=expression.false(),
    )
    tokens: Mapped["Token"] = relationship(back_populates="user")
    stories: Mapped[list["Story"]] = relationship(back_populates="author")

    liked_stories: Mapped[list["Story"]] = relationship(
        secondary="user_story_association",
        back_populates="likers",
    )
