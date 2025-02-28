import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text, UUID
from sqlalchemy import text as text_
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from core.models import Base

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

    author_email: Mapped[str] = mapped_column(ForeignKey("users.email"), nullable=False)
    author: Mapped["User"] = relationship(back_populates="stories")
