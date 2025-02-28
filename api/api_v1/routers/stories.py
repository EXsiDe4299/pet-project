from fastapi import APIRouter, Form, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.dependencies.auth import get_current_user_from_access_token
from api.api_v1.dependencies.stories import get_story_by_uuid_dependency
from api.api_v1.schemas.story import StoryScheme
from api.api_v1.utils.database import (
    get_stories,
    create_story,
    edit_story,
    delete_story,
    like_story,
    get_author_stories,
)
from core.config import settings
from core.models import User, Story
from core.models.db_helper import db_helper

stories_router = APIRouter(
    prefix=settings.stories_router.prefix,
    tags=settings.stories_router.tags,
)


@stories_router.get(
    settings.stories_router.get_stories_endpoint_path,
    response_model=list[StoryScheme],
)
async def get_stories_endpoint(session: AsyncSession = Depends(db_helper.get_session)):
    stories = await get_stories(session=session)
    return stories


@stories_router.get(
    settings.stories_router.get_story_endpoint_path,
    response_model=StoryScheme,
)
async def get_story_endpoint(story: Story = Depends(get_story_by_uuid_dependency)):
    return story


@stories_router.get(
    settings.stories_router.get_author_stories_endpoint_path,
    response_model=list[StoryScheme],
)
async def get_author_stories_endpoint(
    author: str,
    session: AsyncSession = Depends(db_helper.get_session),
):
    stories = await get_author_stories(
        author_username=author,
        session=session,
    )
    return stories


@stories_router.post(
    settings.stories_router.create_story_endpoint_path,
    response_model=StoryScheme,
)
async def create_story_endpoint(
    name: str = Form(),
    text: str = Form(),
    user: User = Depends(get_current_user_from_access_token),
    session: AsyncSession = Depends(db_helper.get_session),
):
    new_story = await create_story(
        name=name,
        text=text,
        author_email=user.email,
        session=session,
    )
    return new_story


@stories_router.put(
    settings.stories_router.edit_story_endpoint_path,
    response_model=StoryScheme,
)
async def edit_story_endpoint(
    story: Story = Depends(get_story_by_uuid_dependency),
    session: AsyncSession = Depends(db_helper.get_session),
    name: str = Form(),
    text: str = Form(),
    user: User = Depends(get_current_user_from_access_token),  # noqa
):
    edited_story = await edit_story(
        name=name,
        text=text,
        story=story,
        session=session,
    )
    return edited_story


@stories_router.delete(settings.stories_router.delete_story_endpoint_path)
async def delete_story_endpoint(
    story: Story = Depends(get_story_by_uuid_dependency),
    session: AsyncSession = Depends(db_helper.get_session),
    user: User = Depends(get_current_user_from_access_token),  # noqa
):
    await delete_story(
        story=story,
        session=session,
    )
    return {"status": "success"}


@stories_router.post(settings.stories_router.like_story_endpoint_path)
async def like_story_endpoint(
    story: Story = Depends(get_story_by_uuid_dependency),
    session: AsyncSession = Depends(db_helper.get_session),
    user: User = Depends(get_current_user_from_access_token),
):
    await like_story(
        story=story,
        user=user,
        session=session,
    )
    return {"status": "success"}
