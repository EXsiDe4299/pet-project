from pydantic import BaseModel

from core.config import settings


class StatusSuccessResponse(BaseModel):
    status: str = "success"


class LoginResponse(StatusSuccessResponse):
    access_token: str
    refresh_token: str
    token_type: str = settings.jwt_auth.token_header_prefix


class RefreshResponse(LoginResponse):
    pass
