from uuid import UUID

from fastapi import APIRouter, Form, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.dependencies.auth import get_current_user_from_access_token
from api.api_v1.utils.database import (
    get_stories,
    get_story,
    create_story,
    edit_story,
    delete_story,
)
from core.models import User
from core.models.db_helper import db_helper

stories_router = APIRouter(
    prefix="/stories",
    tags=["Stories"],
)


@stories_router.get("/")
async def get_stories_endpoint(session: AsyncSession = Depends(db_helper.get_session)):
    stories = await get_stories(session=session)
    return stories


@stories_router.get("/{story_uuid}")
async def get_story_endpoint(
    story_uuid: UUID,
    session: AsyncSession = Depends(db_helper.get_session),
):
    story = await get_story(
        story_uuid=story_uuid,
        session=session,
    )
    return story


@stories_router.post("/")
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


@stories_router.put("/{story_uuid}")
async def edit_story_endpoint(
    story_uuid: UUID,
    session: AsyncSession = Depends(db_helper.get_session),
    name: str = Form(),
    text: str = Form(),
    user: User = Depends(get_current_user_from_access_token),
):
    story = await get_story(
        story_uuid=story_uuid,
        session=session,
    )
    edited_story = await edit_story(
        name=name,
        text=text,
        story=story,
        session=session,
    )
    return edited_story


@stories_router.delete("/{story_uuid}")
async def delete_story_endpoint(
    story_uuid: UUID,
    session: AsyncSession = Depends(db_helper.get_session),
    user: User = Depends(get_current_user_from_access_token),
):
    story = await get_story(
        story_uuid=story_uuid,
        session=session,
    )
    await delete_story(
        story=story,
        session=session,
    )
    return {"status": "success"}
