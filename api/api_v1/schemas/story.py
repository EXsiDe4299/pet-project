import datetime
from uuid import UUID

from pydantic import BaseModel


class StoryScheme(BaseModel):
    id: UUID
    name: str
    likes_number: int
    created_at: datetime.datetime
    author_username: str


class StoryDetailScheme(StoryScheme):
    text: str
