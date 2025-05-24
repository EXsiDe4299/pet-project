import datetime
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text, UUID, func, DateTime
from sqlalchemy import text as text_
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from core.models.base import Base
from core.models.user_story_association import UserStoryAssociation

if TYPE_CHECKING:
    from core.models import User


class Story(Base):
    __tablename__ = "stories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(nullable=False)
    text: Mapped[str] = mapped_column(Text(), nullable=False)
    likes_number: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
        server_default=text_("0"),
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=Base.utc_now,
        server_default=func.now(),
    )

    author_email: Mapped[str] = mapped_column(ForeignKey("users.email"), nullable=False)
    author: Mapped["User"] = relationship(back_populates="stories", lazy="joined")

    likers: Mapped[list["User"]] = relationship(
        secondary=UserStoryAssociation,
        back_populates="liked_stories",
        lazy="joined",
    )

    @validates("likes_number")
    def validate_likes_number(self, key, likes_number):  # noqa
        if likes_number < 0:
            raise ValueError("likes_number value cannot be less than 0")
        return likes_number
