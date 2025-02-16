import logging
from pathlib import Path
from typing import Literal, NamedTuple

from fastapi import HTTPException
from pydantic import BaseModel, PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from starlette import status


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class DatabaseConfig(BaseModel):
    host: str
    port: int
    user: str
    password: str
    database: str
    echo: bool = False
    echo_pool: bool = False
    max_overflow: int = 50
    pool_size: int = 10

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    @computed_field
    @property
    def url(self) -> PostgresDsn:
        return PostgresDsn(
            url=f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}",
        )


class LoggingConfig(BaseModel):
    log_level: Literal[
        "debug",
        "info",
        "warning",
        "error",
        "critical",
    ] = "debug"
    log_format: str = (
        "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
    )
    date_format: str = "%d/%b/%Y %H:%M:%S"

    @property
    def log_level_value(self):
        return logging.getLevelNamesMapping()[self.log_level.upper()]


class JWTAuthConfig(BaseModel):
    private_key_path: Path = (
        Path(__file__).parent.parent / "certificates" / "private.pem"
    )
    public_key_path: Path = Path(__file__).parent.parent / "certificates" / "public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_minutes: int = 60 * 24 * 30
    access_token_type: str = "access"
    refresh_token_type: str = "refresh"
    token_type_payload_key: str = "token_type"
    token_header_prefix: str = "Bearer"


class ExceptionsConfig(NamedTuple):
    already_registered_exc: HTTPException = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="User already registered",
    )
    auth_exc: HTTPException = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect login or password",
    )
    inactive_user_exc: HTTPException = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Inactive user",
    )
    invalid_token_type_exc: HTTPException = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token type",
    )
    invalid_token_exc: HTTPException = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
    )
    email_already_verified_exc: HTTPException = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Email is already verified",
    )
    invalid_code_exc: HTTPException = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid code",
    )
    invalid_email_exc: HTTPException = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Email is invalid or not verified",
    )


class CookieConfig(BaseModel):
    refresh_token_key: str = "refresh_token"
    path: str = "/"
    domain: str | None = None
    secure: bool = False
    httponly: bool = True
    samesite: Literal["lax", "strict", "none"] = "lax"


class MainRouterConfig(BaseModel):
    prefix: str = "/api"


class V1RouterConfig(BaseModel):
    prefix: str = "/v1"


class AuthRouterConfig(BaseModel):
    prefix: str = "/auth"
    tags: list[str] = ["Auth"]
    registration_endpoint_path: str = "/register"
    confirm_email_endpoint_path: str = "/confirm-email"
    login_endpoint_path: str = "/login"
    refresh_endpoint_path: str = "/refresh"
    logout_endpoint_path: str = "/logout"
    send_email_token_endpoint_path: str = "/send-email-verification-token"
    forgot_password_endpoint_path: str = "/forgot-password"
    change_password_endpoint_path: str = "/change-password"


class SmtpConfig(BaseModel):
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool
    USE_CREDENTIALS: bool
    VALIDATE_CERTS: bool


class EmailTokensConfig(BaseModel):
    email_verification_token_exp_minutes: int = 10


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    run: RunConfig = RunConfig()
    db: DatabaseConfig
    log: LoggingConfig = LoggingConfig()
    jwt_auth: JWTAuthConfig = JWTAuthConfig()
    exc: ExceptionsConfig = ExceptionsConfig()
    cookie: CookieConfig = CookieConfig()
    main_router: MainRouterConfig = MainRouterConfig()
    v1_router: V1RouterConfig = V1RouterConfig()
    auth_router: AuthRouterConfig = AuthRouterConfig()
    smtp: SmtpConfig
    email_tokens: EmailTokensConfig = EmailTokensConfig()


settings: Settings = Settings()
