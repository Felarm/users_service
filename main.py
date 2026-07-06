from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger

from auth_session.routers import router as auth_router
from database import redis_client
from users.routers import router as users_router
from exceptions import BaseAppException


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await redis_client.aclose()


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(users_router)


@app.exception_handler(BaseAppException)
async def base_app_exc_handler(request: Request, exc: BaseAppException):
    logger.error(exc.msg)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.msg}
    )
