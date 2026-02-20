import time

import uvicorn
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response
from api.api_v1.dependencies.log_helper import LogHelper
from api.main_router import api_router
from core.config import settings

logger = LogHelper.get_api_logger()

app = FastAPI()

app.include_router(router=api_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Method=%s Path=%s StatusCode=500 Exception=%r",
        request.method,
        request.url.path,
        exc,
        exc_info=exc,
    )
    raise exc


@app.middleware("http")
async def process_time_log_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID")
    LogHelper.set_request_id(request_id)

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
