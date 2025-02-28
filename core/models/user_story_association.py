from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import Base

if TYPE_CHECKING:
    from core.models import User, Story


class UserStoryAssociation(Base):
    __tablename__ = "user_story_association"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_email: Mapped[str] = mapped_column(ForeignKey("users.email"))
    story_id: Mapped[UUID] = mapped_column(ForeignKey("stories.id"))

    user: Mapped["User"] = relationship(overlaps="liked_stories,likers")
    story: Mapped["Story"] = relationship(overlaps="liked_stories,likers")

    __table_args__ = (
        UniqueConstraint(
            "user_email",
            "story_id",
        ),
    )
