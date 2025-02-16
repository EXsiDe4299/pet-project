import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import Base

if TYPE_CHECKING:
    from core.models import User


class Token(Base):
    __tablename__ = "tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(ForeignKey("users.email"))
    user: Mapped["User"] = relationship(back_populates="tokens")

    email_verification_token: Mapped[str] = mapped_column(nullable=True)
    email_verification_token_exp: Mapped[datetime.datetime] = mapped_column(
        nullable=True
    )
    forgot_password_token: Mapped[str] = mapped_column(nullable=True)
    forgot_password_token_exp: Mapped[datetime.datetime] = mapped_column(
        nullable=True
    )

    __table_args__ = (UniqueConstraint("email"),)
