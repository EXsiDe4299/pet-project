from abc import abstractmethod, ABC

from fastapi import Form
from pydantic import BaseModel


class UserBaseScheme(BaseModel):
    username: str
    password: str
    is_active: bool = True


class UserInFromFormScheme(UserBaseScheme, ABC):
    @classmethod
    @abstractmethod
    def as_form(cls):
        pass


class UserRegistrationScheme(UserInFromFormScheme):
    @classmethod
    def as_form(
        cls,
        username: str = Form(
            min_length=3,
            max_length=20,
        ),
        password: str = Form(
            min_length=6,
            max_length=100,
        ),
    ) -> "UserRegistrationScheme":
        return cls(username=username, password=password)


class UserLoginScheme(UserInFromFormScheme):
    @classmethod
    def as_form(
        cls,
        username: str = Form(),
        password: str = Form(),
    ) -> "UserLoginScheme":
        return cls(username=username, password=password)
