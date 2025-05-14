from abc import abstractmethod, ABC

from fastapi import Form
from pydantic import BaseModel, EmailStr

from api.api_v1.schemas.story import StoryScheme


class UserInFromFormScheme(BaseModel, ABC):
    @classmethod
    @abstractmethod
    def as_form(cls):
        pass


class UserRegistrationScheme(UserInFromFormScheme):
    email: EmailStr
    username: str
    password: str

    @classmethod
    def as_form(
        cls,
        username: str = Form(
            default="",
            min_length=3,
            max_length=20,
            regex="[a-zA-Z0-9]+",  # someday I will make a correct regex here
        ),
        email: EmailStr = Form(
            default="",
            regex="[a-zA-Z0-9]+",  # someday I will make a correct regex here
        ),
        password: str = Form(
            default="",
            min_length=6,
            max_length=100,
            regex="[a-zA-Z0-9]+",  # someday I will make a correct regex here
        ),
    ) -> "UserRegistrationScheme":
        return cls(username=username, email=email, password=password)


class UserLoginScheme(UserInFromFormScheme):
    username_or_email: str
    password: str

    @classmethod
    def as_form(
        cls,
        username_or_email: str = Form(default=""),
        password: str = Form(default=""),
    ) -> "UserLoginScheme":
        return cls(username_or_email=username_or_email, password=password)


class UserScheme(BaseModel):
    username: str
    bio: str | None = None
    is_active: bool
    role: str
    avatar_name: str | None = None
    stories: list[StoryScheme]


class UserProfileScheme(UserScheme):
    email: str
    liked_stories: list[StoryScheme]
