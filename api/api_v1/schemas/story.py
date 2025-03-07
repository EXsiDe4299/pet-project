from fastapi import Form
from pydantic import BaseModel, UUID4


class BasicStoryScheme(BaseModel):
    name: str
    text: str


class AuthorScheme(BaseModel):
    username: str


class StoryScheme(BasicStoryScheme):
    id: UUID4
    likes_number: int
    author: AuthorScheme


class StoryInScheme(BasicStoryScheme):
    @classmethod
    def as_form(
        cls,
        name: str = Form(),
        text: str = Form(),
    ) -> "StoryInScheme":
        return cls(
            name=name,
            text=text,
        )
