from pydantic import BaseModel, UUID4


class AuthorScheme(BaseModel):
    username: str


class StoryScheme(BaseModel):
    id: UUID4
    likes_number: int
    name: str
    text: str
    author: AuthorScheme
