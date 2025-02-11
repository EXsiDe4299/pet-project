from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import expression

from core.models.base import Base


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(20), primary_key=True)
    hashed_password: Mapped[bytes] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
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
    email_verification_token: Mapped[str] = mapped_column(nullable=True)
