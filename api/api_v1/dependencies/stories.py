from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.dependencies.database.db_helper import db_helper
from api.api_v1.exceptions.http_exceptions import StoryNotFound
from api.api_v1.utils.database import get_story_by_uuid
from core.models import Story


class GetStoryByUUID:
    def __init__(
        self,
        load_author: bool = False,
        load_likers: bool = False,
    ):
        self.load_author: bool = load_author
        self.load_likers: bool = load_likers

    async def __call__(
        self,
        story_uuid: UUID,
        session: AsyncSession = Depends(db_helper.get_session),
    ) -> Story:
        story = await get_story_by_uuid(
            story_uuid=story_uuid,
            session=session,
            load_author=self.load_author,
            load_likers=self.load_likers,
        )
        if story is None:
            raise StoryNotFound()
        return story


get_story_by_uuid_dependency = GetStoryByUUID()
get_story_by_uuid_dependency_with_likers = GetStoryByUUID(
    load_likers=True,
)
