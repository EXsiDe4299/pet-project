import uvicorn
from fastapi import FastAPI

from api.main_router import api_router
from core.config import settings

app = FastAPI()

app.include_router(router=api_router, prefix='/api')

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
