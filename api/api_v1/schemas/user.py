from abc import abstractmethod, ABC

from fastapi import Form
from pydantic import BaseModel, EmailStr


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
            min_length=3,
            max_length=20,
        ),
        email: EmailStr = Form(),
        password: str = Form(
            min_length=6,
            max_length=100,
        ),
    ) -> "UserRegistrationScheme":
        return cls(username=username, email=email, password=password)


class UserLoginScheme(UserInFromFormScheme):
    username_or_email: str
    password: str

    @classmethod
    def as_form(
        cls,
        username_or_email: str = Form(),
        password: str = Form(),
    ) -> "UserLoginScheme":
        return cls(username_or_email=username_or_email, password=password)
