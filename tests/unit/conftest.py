import asyncio
import datetime
from asyncio import AbstractEventLoop
from unittest.mock import AsyncMock, Mock, MagicMock, patch

import pytest
from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture(scope="session")
def event_loop(request) -> AbstractEventLoop:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture()
def mock_db_session() -> AsyncMock:
    return AsyncMock(spec=AsyncSession)


@pytest.fixture()
def mock_background_tasks() -> Mock:
    return Mock(spec=BackgroundTasks)


@pytest.fixture()
def mock_fastmail() -> MagicMock:
    with patch("api.api_v1.utils.email.fm") as mock:
        yield mock


@pytest.fixture()
def mock_datetime_now(monkeypatch):
    fixed_now = datetime.datetime(
        year=2025,
        month=1,
        day=1,
        hour=12,
        minute=0,
        second=0,
        tzinfo=datetime.UTC,
    )

    class MockDateTime:
        @classmethod
        def now(cls, tz=None):
            return fixed_now

    monkeypatch.setattr(target=datetime, name="datetime", value=MockDateTime)
    return fixed_now
