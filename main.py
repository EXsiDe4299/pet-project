from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from api.main_router import api_router
from core.config import settings
from core.models.db_helper import db_helper


@asynccontextmanager
async def lifespan(application: FastAPI):
    yield
    await db_helper.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(router=api_router, prefix='/api')

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
