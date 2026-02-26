import logging
import os
from contextvars import ContextVar
from os import PathLike

from core.config import settings


class LogHelper:
    _instance: LogHelper | None = None
    _loggers: dict[str, logging.Logger] = {}
    _request_id_var: ContextVar = ContextVar("request_id", default=None)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def setup_logger(
        cls,
        name: str,
        filename: str | PathLike[str],
        level: int = settings.log.log_level_value,
    ) -> logging.Logger:
        if name in cls._loggers:
            return cls._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(level)

        class RequestIdFormatter(logging.Formatter):
            def format(self, record) -> str:
                request_id = cls._request_id_var.get()
                if request_id is not None:
                    record.request_id = request_id
                    return f"[{request_id}] {super().format(record)}"
                return super().format(record)

        formatter = RequestIdFormatter(
            fmt=settings.log.log_format,
            datefmt=settings.log.date_format,
        )

        handler = (
            logging.StreamHandler()
            if os.environ.get("TESTING", "")
            else logging.FileHandler(filename)
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        cls._loggers[name] = logger
        return logger

    @classmethod
    def get_api_logger(cls) -> logging.Logger:
        return cls.setup_logger(
            "api",
            filename=settings.log.api_log_file,
        )

    @classmethod
    def get_app_logger(cls) -> logging.Logger:
        return cls.setup_logger(
            "app",
            filename=settings.log.app_log_file,
        )

    @classmethod
    def set_request_id(cls, request_id: str | None) -> None:
        cls._request_id_var.set(request_id)

    @classmethod
    def get_request_id(cls) -> str | None:
        return cls._request_id_var.get()
