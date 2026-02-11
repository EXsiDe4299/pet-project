from fastapi import HTTPException
from starlette import status


class InvalidAvatarFormat(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: str = "Invalid file format",
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
        )


class InvalidAvatarSize(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: str = "Invalid image size",
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
        )


class AvatarNotFound(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_404_NOT_FOUND,
        detail: str = "Avatar not found",
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
        )


class InvalidJWT(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_401_UNAUTHORIZED,
        detail: str = "Invalid token",
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
        )


class InvalidJWTType(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_401_UNAUTHORIZED,
        detail: str = "Invalid token type",
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
        )


class InactiveUser(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_403_FORBIDDEN,
        detail: str = "Inactive user",
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
        )


class InvalidEmail(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: str = "Email is invalid or not verified",
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
        )


class AlreadyRegistered(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_409_CONFLICT,
        detail: str = "User already registered",
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
        )


class InvalidConfirmEmailCode(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: str = "Invalid confirm email code",
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
        )


class InvalidChangePasswordCode(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: str = "Invalid change password code",
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
        )


class EmailAlreadyVerified(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_409_CONFLICT,
        detail: str = "Email already verified",
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
        )


class InvalidCredentials(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_401_UNAUTHORIZED,
        detail: str = "Invalid credentials",
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
        )


class StoryNotFound(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_404_NOT_FOUND,
        detail: str = "Story not found",
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
        )


class UserNotFound(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_404_NOT_FOUND,
        detail: str = "User not found",
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
        )


class UnsupportedAvatarExtension(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail: str = "Unsupported avatar extension",
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
        )


class ManageOtherStories(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_403_FORBIDDEN,
        detail: str = "You can manage only your own stories",
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
        )


class AdminOrSuperAdminRequired(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_403_FORBIDDEN,
        detail: str = "Only admin or super admin can perform this action",
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
        )


class CannotModifySelf(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_403_FORBIDDEN,
        detail: str = "You cannot do this to yourself",
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
        )


class SuperAdminCanModifyOnlyAdminsOrUsers(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_403_FORBIDDEN,
        detail: str = "Super admins can modify only admins or users",
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
        )


class AdminCanModifyOnlyUsers(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_403_FORBIDDEN,
        detail: str = "Admins can modify only users",
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
        )


class UserAlreadyBlocked(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: str = "User is already blocked",
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
        )


class UserIsNotBlocked(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: str = "User is not blocked",
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
        )
