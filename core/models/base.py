import datetime

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

from core.config import settings


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention=settings.db.naming_convention,
    )

    @staticmethod
    def utc_now():
        return datetime.datetime.now(datetime.UTC)
