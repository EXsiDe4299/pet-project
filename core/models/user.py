import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
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

    username: Mapped[str] = mapped_column(String(150), primary_key=True)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
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
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=Role.USER.value,
        server_default=Role.USER.value,
    )
    registered_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=Base.utc_now,
        server_default=func.now(),
    )

    tokens: Mapped["Token"] = relationship(back_populates="user")
    stories: Mapped[list["Story"]] = relationship(back_populates="author")

    liked_stories: Mapped[list["Story"]] = relationship(
        secondary=UserStoryAssociation,
        back_populates="likers",
    )

    @validates("role")
    def validate_role(self, key, role):
        if role not in Role:
            raise ValueError(f"{role} doesn't exists in Role enum")
        return role

    def __str__(self):
        return (
            f"{self.__class__.__name__}("
            f"username={self.username!r}, "
            f"email={self.email!r}, "
            f"role={self.role!r}, "
            f"is_active={self.is_active}, "
            f"is_email_verified={self.is_email_verified}, "
            f"registered_at={self.registered_at}"
            f")"
        )

    def __repr__(self):
        return str(self)
