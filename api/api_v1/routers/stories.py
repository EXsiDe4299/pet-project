from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.api_v1.dependencies.auth.auth import get_user_from_access_token
from api.api_v1.dependencies.stories import get_story_by_uuid_dependency
from api.api_v1.exceptions.http_exceptions import ManageOtherStories
from api.api_v1.schemas.story import StoryScheme, StoryInScheme, DeleteStoryResponse
from api.api_v1.utils.database import (
    get_stories,
    create_story,
    edit_story,
    delete_story,
    like_story,
    get_author_stories,
    get_stories_by_name_or_text,
)
from core.config import settings
from core.models import User, Story
from api.api_v1.dependencies.database.db_helper import db_helper

stories_router = APIRouter(
    prefix=settings.stories_router.prefix,
    tags=settings.stories_router.tags,
)


@stories_router.get(
    settings.stories_router.get_stories_endpoint_path,
    response_model=list[StoryScheme],
    status_code=status.HTTP_200_OK,
)
async def get_stories_endpoint(
    session: AsyncSession = Depends(db_helper.get_session),
    page: int = 1,
):
    stories = await get_stories(
        session=session,
        page=page,
    )
    return stories


@stories_router.get(
    settings.stories_router.get_stories_by_name_or_text_endpoint_path,
    response_model=list[StoryScheme],
    status_code=status.HTTP_200_OK,
)
async def get_stories_by_name_or_text_endpoint(
    query: str,
    session: AsyncSession = Depends(db_helper.get_session),
    page: int = 1,
):
    stories = await get_stories_by_name_or_text(
        query=query,
        session=session,
        page=page,
    )
    return stories


@stories_router.get(
    settings.stories_router.get_story_endpoint_path,
    response_model=StoryScheme,
    status_code=status.HTTP_200_OK,
)
async def get_story_endpoint(story: Story = Depends(get_story_by_uuid_dependency)):
    return story


@stories_router.get(
    settings.stories_router.get_author_stories_endpoint_path,
    response_model=list[StoryScheme],
    status_code=status.HTTP_200_OK,
)
async def get_author_stories_endpoint(
    author: str,
    session: AsyncSession = Depends(db_helper.get_session),
    page: int = 1,
):
    stories = await get_author_stories(
        author_username=author,
        session=session,
        page=page,
    )
    return stories


@stories_router.post(
    settings.stories_router.create_story_endpoint_path,
    response_model=StoryScheme,
    status_code=status.HTTP_201_CREATED,
)
async def create_story_endpoint(
    story_data: StoryInScheme = Depends(StoryInScheme.as_form),
    user: User = Depends(get_user_from_access_token),
    session: AsyncSession = Depends(db_helper.get_session),
):
    new_story = await create_story(
        name=story_data.name,
        text=story_data.text,
        author_email=user.email,
        session=session,
    )
    return new_story


@stories_router.patch(
    settings.stories_router.edit_story_endpoint_path,
    response_model=StoryScheme,
    status_code=status.HTTP_200_OK,
)
async def edit_story_endpoint(
    story: Story = Depends(get_story_by_uuid_dependency),
    session: AsyncSession = Depends(db_helper.get_session),
    story_data: StoryInScheme = Depends(StoryInScheme.as_form),
    user: User = Depends(get_user_from_access_token),
):
    if story not in user.stories:
        raise ManageOtherStories()
    edited_story = await edit_story(
        name=story_data.name,
        text=story_data.text,
        story=story,
        session=session,
    )
    return edited_story


@stories_router.delete(
    settings.stories_router.delete_story_endpoint_path,
    response_model=DeleteStoryResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_story_endpoint(
    story: Story = Depends(get_story_by_uuid_dependency),
    session: AsyncSession = Depends(db_helper.get_session),
    user: User = Depends(get_user_from_access_token),
):
    if story not in user.stories:
        raise ManageOtherStories()
    await delete_story(
        story=story,
        session=session,
    )
    return DeleteStoryResponse()


@stories_router.post(
    settings.stories_router.like_story_endpoint_path,
    response_model=StoryScheme,
    status_code=status.HTTP_200_OK,
)
async def like_story_endpoint(
    story: Story = Depends(get_story_by_uuid_dependency),
    session: AsyncSession = Depends(db_helper.get_session),
    user: User = Depends(get_user_from_access_token),
):
    liked_story = await like_story(
        story=story,
        user=user,
        session=session,
    )
    return liked_story
