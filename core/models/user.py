import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import expression

from core.models.base import Base
from core.models.user_story_association import UserStoryAssociation

if TYPE_CHECKING:
    from core.models import Token, Story


class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    hashed_password: Mapped[bytes] = mapped_column(nullable=False)
    bio: Mapped[str | None] = mapped_column(
        Text(),
        nullable=True,
    )
    avatar_name: Mapped[str | None] = mapped_column(nullable=True)
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
    role: Mapped[Role] = mapped_column(
        String(50),
        nullable=False,
        default=Role.USER,
        server_default=Role.USER.value,
    )
    registered_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=Base.utc_now,
        server_default=func.now(),
    )

    tokens: Mapped["Token"] = relationship(back_populates="user", lazy="joined")
    stories: Mapped[list["Story"]] = relationship(
        back_populates="author", lazy="selectin"
    )

    liked_stories: Mapped[list["Story"]] = relationship(
        secondary=UserStoryAssociation,
        back_populates="likers",
        lazy="selectin",
    )
