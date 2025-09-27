import logging
import string
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, PostgresDsn, computed_field, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


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


class RedisConfig(BaseModel):
    host: str
    port: int
    db: int
    decode_responses: bool = False

    @computed_field
    @property
    def url(self) -> RedisDsn:
        return RedisDsn(
            url=f"redis://{self.host}:{self.port}/{self.db}?decode_responses={self.decode_responses}"
        )


class LoggingConfig(BaseModel):
    log_level: Literal[
        "debug",
        "info",
        "warning",
        "error",
        "critical",
    ] = "info"
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


class StoriesRouterConfig(BaseModel):
    prefix: str = "/stories"
    tags: list[str] = ["Stories"]
    get_stories_endpoint_path: str = "/all"
    get_story_endpoint_path: str = "/{story_uuid}"
    get_stories_by_name_or_text_endpoint_path: str = "/search"
    get_author_stories_endpoint_path: str = "/"
    create_story_endpoint_path: str = "/"
    edit_story_endpoint_path: str = "/{story_uuid}"
    delete_story_endpoint_path: str = "/{story_uuid}"
    like_story_endpoint_path: str = "/{story_uuid}/like"


class UsersRouterConfig(BaseModel):
    prefix: str = "/users"
    tags: list[str] = ["Users"]
    get_user_endpoint_path: str = "/"
    get_profile_endpoint_path: str = "/profile"
    edit_profile_endpoint_path: str = "/edit-profile"
    get_avatar_endpoint_path: str = "/avatar"


class AdminRouterConfig(BaseModel):
    prefix: str = "/admin"
    tags: list[str] = ["Admin"]
    get_active_users_endpoint_path: str = "/active-users"
    get_inactive_users_endpoint_path: str = "/inactive-users"
    make_admin_endpoint_path: str = "/make-admin"
    demote_admin_endpoint_path: str = "/demote-admin"
    block_user_endpoint_path: str = "/block-user"
    unblock_user_endpoint_path: str = "/unblock-user"


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
    token_length: int = 6
    token_symbols: str = string.ascii_lowercase + string.digits
    email_verification_token_exp_minutes: int = 10
    forgot_password_token_exp_minutes: int = 10


class AvatarConfig(BaseModel):
    avatars_dir: Path = Path(__file__).parent.parent / "avatars"
    allowed_extensions_to_mime: dict[str, str] = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
    }
    size: tuple[int, int] = (200, 200)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    run: RunConfig = RunConfig()
    db: DatabaseConfig
    redis: RedisConfig
    log: LoggingConfig = LoggingConfig()
    jwt_auth: JWTAuthConfig = JWTAuthConfig()
    cookie: CookieConfig = CookieConfig()
    main_router: MainRouterConfig = MainRouterConfig()
    v1_router: V1RouterConfig = V1RouterConfig()
    auth_router: AuthRouterConfig = AuthRouterConfig()
    users_router: UsersRouterConfig = UsersRouterConfig()
    admin_router: AdminRouterConfig = AdminRouterConfig()
    smtp: SmtpConfig
    email_tokens: EmailTokensConfig = EmailTokensConfig()
    stories_router: StoriesRouterConfig = StoriesRouterConfig()
    avatar: AvatarConfig = AvatarConfig()


settings: Settings = Settings()
