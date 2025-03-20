from fastapi import Depends
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.exceptions.http_exceptions import StoryNotFound
from api.api_v1.utils.database import get_story_by_uuid
from core.models import Story
from core.models.db_helper import db_helper


async def get_story_by_uuid_dependency(
    story_uuid: UUID4,
    session: AsyncSession = Depends(db_helper.get_session),
) -> Story:
    story = await get_story_by_uuid(
        story_uuid=story_uuid,
        session=session,
    )
    if story is None:
        raise StoryNotFound()
    return story
