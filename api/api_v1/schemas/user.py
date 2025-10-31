import datetime

from pydantic import BaseModel

from api.api_v1.schemas.story import StoryScheme


class UserScheme(BaseModel):
    username: str
    bio: str | None = None
    is_active: bool
    role: str
    registered_at: datetime.datetime
    avatar_name: str | None = None
    stories: list[StoryScheme]


class UserProfileScheme(UserScheme):
    email: str
    liked_stories: list[StoryScheme]
