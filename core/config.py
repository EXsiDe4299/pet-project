import logging
from typing import Literal

from pydantic import BaseModel, PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RunConfig(BaseModel):
    host: str = '0.0.0.0'
    port: int = 8000


class LoggingConfig(BaseModel):
    log_level: Literal[
        'debug',
        'info',
        'warning',
        'error',
        'critical',
    ] = 'debug'
    log_format: str = '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s'
    date_format: str = "%d/%b/%Y %H:%M:%S"

    @property
    def log_level_value(self):
        return logging.getLevelNamesMapping()[self.log_level.upper()]


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
        "pk": "pk_%(table_name)s"
    }

    @computed_field
    @property
    def url(self) -> PostgresDsn:
        return PostgresDsn(
            url=f'postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}',
        )


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=('.env.template', '.env'),
        case_sensitive=False,
        env_nested_delimiter='__',
        env_prefix='APP_CONFIG__'
    )
    run: RunConfig = RunConfig()
    db: DatabaseConfig
    log: LoggingConfig = LoggingConfig()


settings: Settings = Settings()
