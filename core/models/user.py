from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import expression

from core.models.base import Base

if TYPE_CHECKING:
    from core.models import Token


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    hashed_password: Mapped[bytes] = mapped_column(nullable=False)
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
