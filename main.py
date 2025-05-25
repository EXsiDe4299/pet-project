import logging
import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response

from api.main_router import api_router
from core.config import settings
from core.models.db_helper import db_helper

logging.basicConfig(
    level=settings.log.log_level_value,
    format=settings.log.log_format,
    datefmt=settings.log.date_format,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    yield
    await db_helper.dispose()  # just in case


app = FastAPI(lifespan=lifespan)

app.include_router(router=api_router)


@app.middleware("http")
async def process_time_log_middleware(request: Request, call_next):
    start_time = time.time()
    response: Response = await call_next(request)
    process_time = round(time.time() - start_time, 3)
    logger.info(
        "Method=%s Path=%s StatusCode=%s ProcessTime=%s",
        request.method,
        request.url.path,
        response.status_code,
        process_time,
    )
    return response


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
        access_log=False,
    )
