from pydantic import BaseModel

from core.config import settings


class BaseAuthResponse(BaseModel):
    status: str = "success"


class RegistrationResponse(BaseAuthResponse):
    pass


class ConfirmEmailResponse(BaseAuthResponse):
    pass


class ResendingEmailTokenResponse(BaseAuthResponse):
    pass


class LoginResponse(BaseAuthResponse):
    access_token: str
    refresh_token: str
    token_type: str = settings.jwt_auth.token_header_prefix


class RefreshResponse(LoginResponse):
    pass


class LogoutResponse(BaseAuthResponse):
    pass
